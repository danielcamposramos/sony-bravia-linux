// Entity trace for a SourceTV demo (VR Stereo Spectator, 2026-09-28): every
// update for an entity the client never created (the condition behind
// "Host_Error: CL_PreserveExistingEntity: missing client entity"), and every
// event of one entity when its index is given.
// Usage: entity_trace <demo.dem> [entity index]
use std::collections::HashMap;
use std::env;
use std::fs;

use main_error::MainError;
use tf_demo_parser::demo::data::DemoTick;
use tf_demo_parser::demo::message::packetentities::UpdateType;
use tf_demo_parser::demo::message::Message;
use tf_demo_parser::demo::parser::MessageHandler;
use tf_demo_parser::MessageType;
pub use tf_demo_parser::{Demo, DemoParser, ParserState};

fn main() -> Result<(), MainError> {
    let args: Vec<_> = env::args().collect();
    let file = fs::read(&args[1])?;
    let target: Option<u32> = args.get(2).map(|s| s.parse().expect("entity index"));
    let demo = Demo::new(&file);
    let trace = Trace {
        target,
        known: HashMap::new(),
        reported: 0,
        messages: 0,
        counts: HashMap::new(),
    };
    let parser = DemoParser::new_with_analyser(demo.get_stream(), trace);
    match parser.parse() {
        Ok((_, out)) => println!("{out}"),
        Err(e) => println!("parser stopped: {e}"),
    }
    Ok(())
}

struct Trace {
    target: Option<u32>,
    known: HashMap<u32, String>,
    reported: u32,
    messages: u32,
    // per entity: (class, enters, preserves, leaves, deletes)
    counts: HashMap<u32, (String, u32, u32, u32, u32)>,
}

impl MessageHandler for Trace {
    type Output = String;

    fn does_handle(message_type: MessageType) -> bool {
        matches!(message_type, MessageType::PacketEntities)
    }

    fn handle_message(&mut self, message: &Message, tick: DemoTick, state: &ParserState) {
        let Message::PacketEntities(msg) = message else { return };
        self.messages += 1;
        let tick = u32::from(tick);
        for e in &msg.entities {
            let idx = u32::from(e.entity_index);
            let class = state
                .server_classes
                .get(usize::from(e.server_class))
                .map(|c| c.name.as_str().to_string())
                .unwrap_or_else(|| format!("class {}", u16::from(e.server_class)));
            let c = self.counts.entry(idx).or_insert((class.clone(), 0, 0, 0, 0));
            c.0 = class.clone();
            match e.update_type {
                UpdateType::Enter => c.1 += 1,
                UpdateType::Preserve => c.2 += 1,
                UpdateType::Leave => c.3 += 1,
                UpdateType::Delete => c.4 += 1,
            }
            match e.update_type {
                UpdateType::Enter => {
                    self.known.insert(idx, class.clone());
                }
                UpdateType::Preserve | UpdateType::Leave => {
                    if !self.known.contains_key(&idx) && self.reported < 50 {
                        self.reported += 1;
                        println!(
                            "tick {tick}: {:?} for entity {idx} never created (class {class}, message delta {:?})",
                            e.update_type, msg.delta
                        );
                    }
                }
                UpdateType::Delete => {
                    self.known.remove(&idx);
                }
            }
            if Some(idx) == self.target {
                println!(
                    "tick {tick}: entity {idx} {:?} class {class} in_pvs {} serial {} props {} (message delta {:?}, baseline {:?}, updated baseline {})",
                    e.update_type,
                    e.in_pvs,
                    e.serial_number,
                    e.props.len(),
                    msg.delta,
                    msg.base_line,
                    msg.updated_base_line
                );
            }
        }
        for r in &msg.removed_entities {
            let i = u32::from(*r);
            if Some(i) == self.target {
                println!("tick {tick}: entity {i} removed (message delta {:?})", msg.delta);
            }
            self.known.remove(&i);
        }
    }

    fn into_output(self, _state: &ParserState) -> Self::Output {
        let mut v: Vec<_> = self.counts.iter().collect();
        v.sort_by_key(|(i, _)| **i);
        let mut s = String::from("entity class enters preserves leaves deletes\n");
        for (i, (class, en, pr, le, de)) in v {
            if *en > 3 || *i < 5 {
                s += &format!("{i} {class} {en} {pr} {le} {de}\n");
            }
        }
        s + &format!(
            "done: {} packet-entities messages, {} updates for entities never created",
            self.messages, self.reported
        )
    }
}

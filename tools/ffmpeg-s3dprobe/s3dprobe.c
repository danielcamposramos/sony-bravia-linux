/* s3dprobe: decode the first video frames and print every Stereo 3D side-data
 * entry on each, to show which layout wins when container and SEI disagree. */
#include <stdio.h>
#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libavutil/opt.h>
#include <libavutil/stereo3d.h>

int main(int argc, char **argv)
{
    AVFormatContext *fmt = NULL;
    const AVCodec *dec;
    AVCodecContext *c;
    AVPacket *pkt = av_packet_alloc();
    AVFrame *f = av_frame_alloc();
    int idx, n = 0;

    if (avformat_open_input(&fmt, argv[1], NULL, NULL) < 0 ||
        avformat_find_stream_info(fmt, NULL) < 0)
        return 1;
    idx = av_find_best_stream(fmt, AVMEDIA_TYPE_VIDEO, -1, -1, &dec, 0);
    c = avcodec_alloc_context3(dec);
    avcodec_parameters_to_context(c, fmt->streams[idx]->codecpar);
    if (argc > 2)
        av_opt_set(c, "side_data_prefer_packet", argv[2], 0);
    if (avcodec_open2(c, dec, NULL) < 0)
        return 1;
    while (n < 3 && av_read_frame(fmt, pkt) >= 0) {
        if (pkt->stream_index == idx && avcodec_send_packet(c, pkt) >= 0)
            while (n < 3 && avcodec_receive_frame(c, f) >= 0) {
                printf("frame %d:", n++);
                for (int i = 0; i < f->nb_side_data; i++)
                    if (f->side_data[i]->type == AV_FRAME_DATA_STEREO3D)
                        printf(" [%s]", av_stereo3d_type_name(
                            ((AVStereo3D *)f->side_data[i]->data)->type));
                printf("\n");
            }
        av_packet_unref(pkt);
    }
    return 0;
}

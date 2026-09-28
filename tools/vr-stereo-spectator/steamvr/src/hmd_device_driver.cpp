//============ Copyright (c) Valve Corporation, All rights reserved. ============
// Changes for 3D displays (sony-bravia-linux, 2026-09-28): the driver's name,
// the display's layout (side by side or top and bottom), the eyes' shifted
// views meeting at the screen plane, a fixed head, the display's refresh rate.
#include "hmd_device_driver.h"

#include "driverlog.h"
#include "vrmath.h"
#include <math.h>
#include <string.h>

// Let's create some variables for strings used in getting settings.
// This is the section where all of the settings we want are stored. A section name can be anything,
// but if you want to store driver specific settings, it's best to namespace the section with the driver identifier
// ie "<my_driver>_<section>" to avoid collisions
static const char *my_hmd_main_settings_section = "driver_stereodisplay";
static const char *my_hmd_display_settings_section = "stereodisplay_display";

MyHMDControllerDeviceDriver::MyHMDControllerDeviceDriver()
{
	// Keep track of whether Activate() has been called
	is_active_ = false;

	// We have our model number and serial number stored in SteamVR settings. We need to get them and do so here.
	// Other IVRSettings methods (to get int32, floats, bools) return the data, instead of modifying, but strings are
	// different.
	char model_number[ 1024 ];
	vr::VRSettings()->GetString( my_hmd_main_settings_section, "model_number", model_number, sizeof( model_number ) );
	my_hmd_model_number_ = model_number;

	// Get our serial number depending on our "handedness"
	char serial_number[ 1024 ];
	vr::VRSettings()->GetString( my_hmd_main_settings_section, "serial_number", serial_number, sizeof( serial_number ) );
	my_hmd_serial_number_ = serial_number;

	// Here's an example of how to use our logging wrapper around IVRDriverLog
	// In SteamVR logs (SteamVR Hamburger Menu > Developer Settings > Web console) drivers have a prefix of
	// "<driver_name>:". You can search this in the top search bar to find the info that you've logged.
	DriverLog( "My Dummy HMD Model Number: %s", my_hmd_model_number_.c_str() );
	DriverLog( "My Dummy HMD Serial Number: %s", my_hmd_serial_number_.c_str() );

	// Display settings
	MyHMDDisplayDriverConfiguration display_configuration{};
	display_configuration.window_x = vr::VRSettings()->GetInt32( my_hmd_display_settings_section, "window_x" );
	display_configuration.window_y = vr::VRSettings()->GetInt32( my_hmd_display_settings_section, "window_y" );

	display_configuration.window_width = vr::VRSettings()->GetInt32( my_hmd_display_settings_section, "window_width" );
	display_configuration.window_height = vr::VRSettings()->GetInt32( my_hmd_display_settings_section, "window_height" );

	display_configuration.render_width = vr::VRSettings()->GetInt32( my_hmd_display_settings_section, "render_width" );
	display_configuration.render_height = vr::VRSettings()->GetInt32( my_hmd_display_settings_section, "render_height" );

	// The 3D display: its packing, the field of view across one eye's
	// picture, and how far away the screen plane (zero parallax) sits.
	char layout[ 16 ] = "sbs";
	vr::VRSettings()->GetString( my_hmd_display_settings_section, "layout", layout, sizeof( layout ) );
	display_configuration.top_and_bottom = strcmp( layout, "tab" ) == 0;
	float fov_h = vr::VRSettings()->GetFloat( my_hmd_display_settings_section, "fov_horizontal_degrees" );
	if ( fov_h <= 10.f || fov_h >= 170.f )
		fov_h = 90.f;
	display_configuration.tan_half_fov_h = tanf( fov_h * 3.14159265f / 360.f );
	display_configuration.screen_distance = vr::VRSettings()->GetFloat( my_hmd_display_settings_section, "screen_distance_meters" );
	if ( display_configuration.screen_distance <= 0.1f )
		display_configuration.screen_distance = 2.f;
	display_configuration.ipd = vr::VRSettings()->GetFloat( vr::k_pch_SteamVR_Section, vr::k_pch_SteamVR_IPD_Float );
	if ( display_configuration.ipd <= 0.f )
		display_configuration.ipd = 0.064f;
	head_height_ = vr::VRSettings()->GetFloat( my_hmd_display_settings_section, "head_height_meters" );
	if ( head_height_ <= 0.f )
		head_height_ = 1.6f;
	display_frequency_ = vr::VRSettings()->GetFloat( my_hmd_display_settings_section, "display_frequency" );
	if ( display_frequency_ <= 0.f )
		display_frequency_ = 60.f;
	DriverLog( "3D display: %s, %dx%d window at %d,%d, eyes rendered %dx%d, %.0f degrees across, screen plane at %.2f m, ipd %.3f m, %.0f Hz",
		display_configuration.top_and_bottom ? "top and bottom" : "side by side",
		display_configuration.window_width, display_configuration.window_height,
		display_configuration.window_x, display_configuration.window_y,
		display_configuration.render_width, display_configuration.render_height,
		fov_h, display_configuration.screen_distance, display_configuration.ipd, display_frequency_ );

	// Instantiate our display component
	my_display_component_ = std::make_unique< MyHMDDisplayComponent >( display_configuration );
}

//-----------------------------------------------------------------------------
// Purpose: This is called by vrserver after our
//  IServerTrackedDeviceProvider calls IVRServerDriverHost::TrackedDeviceAdded.
//-----------------------------------------------------------------------------
vr::EVRInitError MyHMDControllerDeviceDriver::Activate( uint32_t unObjectId )
{
	// Let's keep track of our device index. It'll be useful later.
	// Also, if we re-activate, be sure to set this.
	device_index_ = unObjectId;

	// Set a member to keep track of whether we've activated yet or not
	is_active_ = true;

	// For keeping track of frame number for animating motion.
	frame_number_ = 0;

	// Properties are stored in containers, usually one container per device index. We need to get this container to set
	// The properties we want, so we call this to retrieve a handle to it.
	vr::PropertyContainerHandle_t container = vr::VRProperties()->TrackedDeviceToPropertyContainer( device_index_ );

	// Let's begin setting up the properties now we've got our container.
	// A list of properties available is contained in vr::ETrackedDeviceProperty.

	// First, let's set the model number.
	vr::VRProperties()->SetStringProperty( container, vr::Prop_ModelNumber_String, my_hmd_model_number_.c_str() );

	// Next, display settings

	// Get the ipd of the user from SteamVR settings
	const float ipd = vr::VRSettings()->GetFloat( vr::k_pch_SteamVR_Section, vr::k_pch_SteamVR_IPD_Float );
	vr::VRProperties()->SetFloatProperty( container, vr::Prop_UserIpdMeters_Float, ipd );

	// For HMDs, it's required that a refresh rate is set otherwise VRCompositor will fail to start.
	vr::VRProperties()->SetFloatProperty( container, vr::Prop_DisplayFrequency_Float, display_frequency_ );

	// The distance from the user's eyes to the display in meters. This is used for reprojection.
	vr::VRProperties()->SetFloatProperty( container, vr::Prop_UserHeadToEyeDepthMeters_Float, 0.f );

	// How long from the compositor to submit a frame to the time it takes to display it on the screen.
	vr::VRProperties()->SetFloatProperty( container, vr::Prop_SecondsFromVsyncToPhotons_Float, 0.11f );

	// avoid "not fullscreen" warnings from vrmonitor
	vr::VRProperties()->SetBoolProperty( container, vr::Prop_IsOnDesktop_Bool, false );

	vr::VRProperties()->SetBoolProperty(container, vr::Prop_DisplayDebugMode_Bool, true);

	// Now let's set up our inputs
	// This tells the UI what to show the user for bindings for this controller,
	// As well as what default bindings should be for legacy apps.
	// Note, we can use the wildcard {<driver_name>} to match the root folder location
	// of our driver.
	vr::VRProperties()->SetStringProperty( container, vr::Prop_InputProfilePath_String, "{stereodisplay}/input/stereodisplay_profile.json" );

	// Let's set up handles for all of our components.
	// Even though these are also defined in our input profile,
	// We need to get handles to them to update the inputs.
	vr::VRDriverInput()->CreateBooleanComponent( container, "/input/system/touch", &my_input_handles_[ MyComponent_system_touch ] );
	vr::VRDriverInput()->CreateBooleanComponent( container, "/input/system/click", &my_input_handles_[ MyComponent_system_click ] );

	my_pose_update_thread_ = std::thread( &MyHMDControllerDeviceDriver::MyPoseUpdateThread, this );

	// We've activated everything successfully!
	// Let's tell SteamVR that by saying we don't have any errors.
	return vr::VRInitError_None;
}

//-----------------------------------------------------------------------------
// Purpose: If you're an HMD, this is where you would return an implementation
// of vr::IVRDisplayComponent, vr::IVRVirtualDisplay or vr::IVRDirectModeComponent.
//-----------------------------------------------------------------------------
void *MyHMDControllerDeviceDriver::GetComponent( const char *pchComponentNameAndVersion )
{
	if ( strcmp( pchComponentNameAndVersion, vr::IVRDisplayComponent_Version ) == 0 )
	{
		return my_display_component_.get();
	}

	return nullptr;
}

//-----------------------------------------------------------------------------
// Purpose: This is called by vrserver when a debug request has been made from an application to the driver.
// What is in the response and request is up to the application and driver to figure out themselves.
//-----------------------------------------------------------------------------
void MyHMDControllerDeviceDriver::DebugRequest( const char *pchRequest, char *pchResponseBuffer, uint32_t unResponseBufferSize )
{
	if ( unResponseBufferSize >= 1 )
		pchResponseBuffer[ 0 ] = 0;
}

//-----------------------------------------------------------------------------
// Purpose: This is never called by vrserver in recent OpenVR versions,
// but is useful for giving data to vr::VRServerDriverHost::TrackedDevicePoseUpdated.
//-----------------------------------------------------------------------------
vr::DriverPose_t MyHMDControllerDeviceDriver::GetPose()
{
	// Let's retrieve the Hmd pose to base our controller pose off.

	// First, initialize the struct that we'll be submitting to the runtime to tell it we've updated our pose.
	vr::DriverPose_t pose = { 0 };

	// These need to be set to be valid quaternions. The device won't appear otherwise.
	pose.qWorldFromDriverRotation.w = 1.f;
	pose.qDriverFromHeadRotation.w = 1.f;

	pose.qRotation.w = 1.f;

	// A display does not move with the head: the head stays where the
	// viewer sits, at a set height.
	pose.vecPosition[ 0 ] = 0.0f;
	pose.vecPosition[ 1 ] = head_height_;
	pose.vecPosition[ 2 ] = 0.0f;

	// The pose we provided is valid.
	// This should be set is
	pose.poseIsValid = true;

	// Our device is always connected.
	// In reality with physical devices, when they get disconnected,
	// set this to false and icons in SteamVR will be updated to show the device is disconnected
	pose.deviceIsConnected = true;

	// The state of our tracking. For our virtual device, it's always going to be ok,
	// but this can get set differently to inform the runtime about the state of the device's tracking
	// and update the icons to inform the user accordingly.
	pose.result = vr::TrackingResult_Running_OK;

	// For HMDs we want to apply rotation/motion prediction
	// No neck model: the eyes are fixed in front of the screen.
	pose.shouldApplyHeadModel = false;

	return pose;
}

void MyHMDControllerDeviceDriver::MyPoseUpdateThread()
{
	while ( is_active_ )
	{
		// Inform the vrserver that our tracked device's pose has updated, giving it the pose returned by our GetPose().
		vr::VRServerDriverHost()->TrackedDevicePoseUpdated( device_index_, GetPose(), sizeof( vr::DriverPose_t ) );

		// Update our pose every five milliseconds.
		// In reality, you should update the pose whenever you have new data from your device.
		std::this_thread::sleep_for( std::chrono::milliseconds( 5 ) );
	}
}

//-----------------------------------------------------------------------------
// Purpose: This is called by vrserver when the device should enter standby mode.
// The device should be put into whatever low power mode it has.
// We don't really have anything to do here, so let's just log something.
//-----------------------------------------------------------------------------
void MyHMDControllerDeviceDriver::EnterStandby()
{
	DriverLog( "HMD has been put into standby." );
}

//-----------------------------------------------------------------------------
// Purpose: This is called by vrserver when the device should deactivate.
// This is typically at the end of a session
// The device should free any resources it has allocated here.
//-----------------------------------------------------------------------------
void MyHMDControllerDeviceDriver::Deactivate()
{
	// Let's join our pose thread that's running
	// by first checking then setting is_active_ to false to break out
	// of the while loop, if it's running, then call .join() on the thread
	if ( is_active_.exchange( false ) )
	{
		my_pose_update_thread_.join();
	}

	// unassign our controller index (we don't want to be calling vrserver anymore after Deactivate() has been called
	device_index_ = vr::k_unTrackedDeviceIndexInvalid;
}


//-----------------------------------------------------------------------------
// Purpose: This is called by our IServerTrackedDeviceProvider when its RunFrame() method gets called.
// It's not part of the ITrackedDeviceServerDriver interface, we created it ourselves.
//-----------------------------------------------------------------------------
void MyHMDControllerDeviceDriver::MyRunFrame()
{
	frame_number_++;
	// update our inputs here
}


//-----------------------------------------------------------------------------
// Purpose: This is called by our IServerTrackedDeviceProvider when it pops an event off the event queue.
// It's not part of the ITrackedDeviceServerDriver interface, we created it ourselves.
//-----------------------------------------------------------------------------
void MyHMDControllerDeviceDriver::MyProcessEvent( const vr::VREvent_t &vrevent )
{
}


//-----------------------------------------------------------------------------
// Purpose: Our IServerTrackedDeviceProvider needs our serial number to add us to vrserver.
// It's not part of the ITrackedDeviceServerDriver interface, we created it ourselves.
//-----------------------------------------------------------------------------
const std::string &MyHMDControllerDeviceDriver::MyGetSerialNumber()
{
	return my_hmd_serial_number_;
}

//-----------------------------------------------------------------------------
// DISPLAY DRIVER METHOD DEFINITIONS
//-----------------------------------------------------------------------------

MyHMDDisplayComponent::MyHMDDisplayComponent( const MyHMDDisplayDriverConfiguration &config )
	: config_( config )
{
}

//-----------------------------------------------------------------------------
// Purpose: To inform vrcompositor if this display is considered an on-desktop display.
//-----------------------------------------------------------------------------
bool MyHMDDisplayComponent::IsDisplayOnDesktop()
{
	return true;
}

//-----------------------------------------------------------------------------
// Purpose: To as vrcompositor to search for this display.
//-----------------------------------------------------------------------------
bool MyHMDDisplayComponent::IsDisplayRealDisplay()
{
	return false;
}

//-----------------------------------------------------------------------------
// Purpose: To inform the rest of the vr system what the recommended target size should be
//-----------------------------------------------------------------------------
void MyHMDDisplayComponent::GetRecommendedRenderTargetSize( uint32_t *pnWidth, uint32_t *pnHeight )
{
	*pnWidth = config_.render_width;
	*pnHeight = config_.render_height;
}

//-----------------------------------------------------------------------------
// Purpose: To inform vrcompositor how the screens should be organized.
//-----------------------------------------------------------------------------
void MyHMDDisplayComponent::GetEyeOutputViewport( vr::EVREye eEye, uint32_t *pnX, uint32_t *pnY, uint32_t *pnWidth, uint32_t *pnHeight )
{
	// Each eye in half of the window, the left eye first: left in side by
	// side, on top in top and bottom, as HDMI 1.4 packs them. The display
	// stretches each half back to the whole screen.
	bool first = eEye == vr::Eye_Left;
	if ( config_.top_and_bottom )
	{
		*pnX = 0;
		*pnWidth = config_.window_width;
		*pnHeight = config_.window_height / 2;
		*pnY = first ? 0 : config_.window_height / 2;
	}
	else
	{
		*pnY = 0;
		*pnHeight = config_.window_height;
		*pnWidth = config_.window_width / 2;
		*pnX = first ? 0 : config_.window_width / 2;
	}
}

//-----------------------------------------------------------------------------
// Purpose: To inform the compositor what the projection parameters are for this HMD.
//-----------------------------------------------------------------------------
void MyHMDDisplayComponent::GetProjectionRaw( vr::EVREye eEye, float *pfLeft, float *pfRight, float *pfTop, float *pfBottom )
{
	// A window, not a headset (FORMULA.md, section 1): the eyes look straight
	// ahead, half the ipd to each side, and each eye's view is shifted
	// sideways so both frame the same screen at screen_distance, which is
	// where depth is zero. A headset's views are centred on its lenses
	// instead. Each eye's picture fills the whole screen once the display
	// unpacks it, so its height follows the window's shape.
	float t = config_.tan_half_fov_h;
	float v = t * (float)config_.window_height / (float)config_.window_width;
	float shift = ( config_.ipd / 2.f ) / config_.screen_distance;
	if ( eEye == vr::Eye_Left )
		shift = -shift;   // the left eye's view moves toward the centre: to its right
	*pfLeft = -t - shift;
	*pfRight = t - shift;
	*pfTop = -v;
	*pfBottom = v;
}

//-----------------------------------------------------------------------------
// Purpose: To compute the distortion properties for a given uv in an image.
//-----------------------------------------------------------------------------
vr::DistortionCoordinates_t MyHMDDisplayComponent::ComputeDistortion( vr::EVREye eEye, float fU, float fV )
{
	vr::DistortionCoordinates_t coordinates{};
	coordinates.rfBlue[ 0 ] = fU;
	coordinates.rfBlue[ 1 ] = fV;
	coordinates.rfGreen[ 0 ] = fU;
	coordinates.rfGreen[ 1 ] = fV;
	coordinates.rfRed[ 0 ] = fU;
	coordinates.rfRed[ 1 ] = fV;
	return coordinates;
}

//-----------------------------------------------------------------------------
// Purpose: To inform vrcompositor what the window bounds for this virtual HMD are.
//-----------------------------------------------------------------------------
void MyHMDDisplayComponent::GetWindowBounds( int32_t *pnX, int32_t *pnY, uint32_t *pnWidth, uint32_t *pnHeight )
{
	*pnX = config_.window_x;
	*pnY = config_.window_y;
	*pnWidth = config_.window_width;
	*pnHeight = config_.window_height;
}

bool MyHMDDisplayComponent::ComputeInverseDistortion(vr::HmdVector2_t* pResult, vr::EVREye eEye, uint32_t unChannel, float fU, float fV)
{
	//Return false to let SteamVR infer an estimate from ComputeDistortion
	return false;
}
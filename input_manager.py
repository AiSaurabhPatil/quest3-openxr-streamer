import xr
import ctypes

class InputManager:
    def __init__(self, instance, session):
        self.instance = instance
        self.session = session
        self.action_set = None
        self.action_aim_pose = None
        self.action_grip_pose = None
        
        # Button/Analog Actions
        self.action_trigger = None
        self.action_squeeze = None
        self.action_thumbstick = None
        self.action_thumbstick_click = None
        self.action_button_a = None  # Right A
        self.action_button_b = None  # Right B
        self.action_button_x = None  # Left X
        self.action_button_y = None  # Left Y
        self.action_menu = None      # Left Menu
        
        self.ref_space = None
        self.left_aim_space = None
        self.right_aim_space = None
        self.left_grip_space = None
        self.right_grip_space = None
        
        # Hand paths for subactions
        self.left_hand_path = None
        self.right_hand_path = None
        
        # Get xrLocateSpace function pointer
        self.xrLocateSpace = ctypes.cast(
            xr.get_instance_proc_addr(self.instance, "xrLocateSpace"),
            xr.PFN_xrLocateSpace
        )

    def setup_actions(self):
        # Store hand paths for later use
        self.left_hand_path = xr.string_to_path(self.instance, "/user/hand/left")
        self.right_hand_path = xr.string_to_path(self.instance, "/user/hand/right")
        hand_paths = [self.left_hand_path, self.right_hand_path]
        
        self.action_set = xr.create_action_set(
            self.instance,
            xr.ActionSetCreateInfo(
                action_set_name="controller_data",
                localized_action_set_name="Controller Data",
                priority=1,
            )
        )
        
        # Create Pose Actions
        self.action_aim_pose = xr.create_action(
            self.action_set,
            xr.ActionCreateInfo(
                action_type=xr.ActionType.POSE_INPUT,
                action_name="aim_pose",
                localized_action_name="Aim Pose",
                count_subaction_paths=2,
                subaction_paths=hand_paths,
            )
        )
        
        self.action_grip_pose = xr.create_action(
            self.action_set,
            xr.ActionCreateInfo(
                action_type=xr.ActionType.POSE_INPUT,
                action_name="grip_pose",
                localized_action_name="Grip Pose",
                count_subaction_paths=2,
                subaction_paths=hand_paths,
            )
        )
        
        # Create Float Actions (Analog Inputs)
        self.action_trigger = xr.create_action(
            self.action_set,
            xr.ActionCreateInfo(
                action_type=xr.ActionType.FLOAT_INPUT,
                action_name="trigger",
                localized_action_name="Trigger",
                count_subaction_paths=2,
                subaction_paths=hand_paths,
            )
        )
        
        self.action_squeeze = xr.create_action(
            self.action_set,
            xr.ActionCreateInfo(
                action_type=xr.ActionType.FLOAT_INPUT,
                action_name="squeeze",
                localized_action_name="Squeeze",
                count_subaction_paths=2,
                subaction_paths=hand_paths,
            )
        )
        
        self.action_thumbstick = xr.create_action(
            self.action_set,
            xr.ActionCreateInfo(
                action_type=xr.ActionType.VECTOR2F_INPUT,
                action_name="thumbstick",
                localized_action_name="Thumbstick",
                count_subaction_paths=2,
                subaction_paths=hand_paths,
            )
        )
        
        # Create Boolean Actions (Buttons)
        self.action_thumbstick_click = xr.create_action(
            self.action_set,
            xr.ActionCreateInfo(
                action_type=xr.ActionType.BOOLEAN_INPUT,
                action_name="thumbstick_click",
                localized_action_name="Thumbstick Click",
                count_subaction_paths=2,
                subaction_paths=hand_paths,
            )
        )
        
        self.action_button_a = xr.create_action(
            self.action_set,
            xr.ActionCreateInfo(
                action_type=xr.ActionType.BOOLEAN_INPUT,
                action_name="button_a",
                localized_action_name="Button A",
                count_subaction_paths=1,
                subaction_paths=[self.right_hand_path],
            )
        )
        
        self.action_button_b = xr.create_action(
            self.action_set,
            xr.ActionCreateInfo(
                action_type=xr.ActionType.BOOLEAN_INPUT,
                action_name="button_b",
                localized_action_name="Button B",
                count_subaction_paths=1,
                subaction_paths=[self.right_hand_path],
            )
        )
        
        self.action_button_x = xr.create_action(
            self.action_set,
            xr.ActionCreateInfo(
                action_type=xr.ActionType.BOOLEAN_INPUT,
                action_name="button_x",
                localized_action_name="Button X",
                count_subaction_paths=1,
                subaction_paths=[self.left_hand_path],
            )
        )
        
        self.action_button_y = xr.create_action(
            self.action_set,
            xr.ActionCreateInfo(
                action_type=xr.ActionType.BOOLEAN_INPUT,
                action_name="button_y",
                localized_action_name="Button Y",
                count_subaction_paths=1,
                subaction_paths=[self.left_hand_path],
            )
        )
        
        self.action_menu = xr.create_action(
            self.action_set,
            xr.ActionCreateInfo(
                action_type=xr.ActionType.BOOLEAN_INPUT,
                action_name="menu",
                localized_action_name="Menu",
                count_subaction_paths=1,
                subaction_paths=[self.left_hand_path],
            )
        )

        # Suggest Bindings
        self._suggest_bindings()

        # Attach Action Set
        xr.attach_session_action_sets(
            self.session,
            xr.SessionActionSetsAttachInfo(action_sets=[self.action_set])
        )

    def _suggest_bindings(self):
        # Suggest bindings for multiple controller profiles to maximize compatibility
        
        # Oculus Touch Controller Profile (Quest 1/2)
        self._suggest_touch_bindings("/interaction_profiles/oculus/touch_controller")
        
        # Meta Quest Touch Pro Controller (Quest 3/Pro) - may be the one WiVRn reports
        try:
            self._suggest_touch_bindings("/interaction_profiles/meta/touch_controller_plus")
        except Exception as e:
            print(f"Note: Meta Touch Plus profile not available: {e}")
        
        # Also try the FB extension version
        try:
            self._suggest_touch_bindings("/interaction_profiles/facebook/touch_controller_pro")
        except Exception as e:
            print(f"Note: FB Touch Pro profile not available: {e}")
        
        # Khronos Simple Controller (universal fallback)
        try:
            self._suggest_simple_bindings()
        except Exception as e:
            print(f"Note: Simple controller profile not available: {e}")

    def _suggest_touch_bindings(self, profile_name):
        """Suggest bindings for Touch-style controllers"""
        profile_path = xr.string_to_path(self.instance, profile_name)
        xr.suggest_interaction_profile_bindings(
            self.instance,
            xr.InteractionProfileSuggestedBinding(
                interaction_profile=profile_path,
                suggested_bindings=[
                    # Pose Bindings
                    xr.ActionSuggestedBinding(action=self.action_aim_pose, binding=xr.string_to_path(self.instance, "/user/hand/left/input/aim/pose")),
                    xr.ActionSuggestedBinding(action=self.action_aim_pose, binding=xr.string_to_path(self.instance, "/user/hand/right/input/aim/pose")),
                    xr.ActionSuggestedBinding(action=self.action_grip_pose, binding=xr.string_to_path(self.instance, "/user/hand/left/input/grip/pose")),
                    xr.ActionSuggestedBinding(action=self.action_grip_pose, binding=xr.string_to_path(self.instance, "/user/hand/right/input/grip/pose")),
                    # Trigger (Float)
                    xr.ActionSuggestedBinding(action=self.action_trigger, binding=xr.string_to_path(self.instance, "/user/hand/left/input/trigger/value")),
                    xr.ActionSuggestedBinding(action=self.action_trigger, binding=xr.string_to_path(self.instance, "/user/hand/right/input/trigger/value")),
                    # Squeeze/Grip (Float)
                    xr.ActionSuggestedBinding(action=self.action_squeeze, binding=xr.string_to_path(self.instance, "/user/hand/left/input/squeeze/value")),
                    xr.ActionSuggestedBinding(action=self.action_squeeze, binding=xr.string_to_path(self.instance, "/user/hand/right/input/squeeze/value")),
                    # Thumbstick (Vector2f)
                    xr.ActionSuggestedBinding(action=self.action_thumbstick, binding=xr.string_to_path(self.instance, "/user/hand/left/input/thumbstick")),
                    xr.ActionSuggestedBinding(action=self.action_thumbstick, binding=xr.string_to_path(self.instance, "/user/hand/right/input/thumbstick")),
                    # Thumbstick Click (Boolean)
                    xr.ActionSuggestedBinding(action=self.action_thumbstick_click, binding=xr.string_to_path(self.instance, "/user/hand/left/input/thumbstick/click")),
                    xr.ActionSuggestedBinding(action=self.action_thumbstick_click, binding=xr.string_to_path(self.instance, "/user/hand/right/input/thumbstick/click")),
                    # Buttons (Boolean)
                    xr.ActionSuggestedBinding(action=self.action_button_a, binding=xr.string_to_path(self.instance, "/user/hand/right/input/a/click")),
                    xr.ActionSuggestedBinding(action=self.action_button_b, binding=xr.string_to_path(self.instance, "/user/hand/right/input/b/click")),
                    xr.ActionSuggestedBinding(action=self.action_button_x, binding=xr.string_to_path(self.instance, "/user/hand/left/input/x/click")),
                    xr.ActionSuggestedBinding(action=self.action_button_y, binding=xr.string_to_path(self.instance, "/user/hand/left/input/y/click")),
                    xr.ActionSuggestedBinding(action=self.action_menu, binding=xr.string_to_path(self.instance, "/user/hand/left/input/menu/click")),
                ],
            )
        )
        print(f"Suggested bindings for: {profile_name}")

    def _suggest_simple_bindings(self):
        """Suggest bindings for Khronos Simple Controller (fallback)"""
        profile_path = xr.string_to_path(self.instance, "/interaction_profiles/khr/simple_controller")
        xr.suggest_interaction_profile_bindings(
            self.instance,
            xr.InteractionProfileSuggestedBinding(
                interaction_profile=profile_path,
                suggested_bindings=[
                    # Simple controller only has aim pose and select/menu
                    xr.ActionSuggestedBinding(action=self.action_aim_pose, binding=xr.string_to_path(self.instance, "/user/hand/left/input/aim/pose")),
                    xr.ActionSuggestedBinding(action=self.action_aim_pose, binding=xr.string_to_path(self.instance, "/user/hand/right/input/aim/pose")),
                    xr.ActionSuggestedBinding(action=self.action_grip_pose, binding=xr.string_to_path(self.instance, "/user/hand/left/input/grip/pose")),
                    xr.ActionSuggestedBinding(action=self.action_grip_pose, binding=xr.string_to_path(self.instance, "/user/hand/right/input/grip/pose")),
                    # Map trigger to select click (simple controller doesn't have analog trigger)
                    xr.ActionSuggestedBinding(action=self.action_thumbstick_click, binding=xr.string_to_path(self.instance, "/user/hand/left/input/select/click")),
                    xr.ActionSuggestedBinding(action=self.action_thumbstick_click, binding=xr.string_to_path(self.instance, "/user/hand/right/input/select/click")),
                ],
            )
        )
        print("Suggested bindings for: khr/simple_controller")

    def print_current_interaction_profile(self):
        """Query and print the current interaction profile for each hand"""
        try:
            left_path = xr.string_to_path(self.instance, "/user/hand/left")
            right_path = xr.string_to_path(self.instance, "/user/hand/right")
            
            left_profile = xr.get_current_interaction_profile(self.session, left_path)
            right_profile = xr.get_current_interaction_profile(self.session, right_path)
            
            # Convert profile paths back to strings
            if left_profile.interaction_profile != xr.NULL_PATH:
                left_name = xr.path_to_string(self.instance, left_profile.interaction_profile)
                print(f"Left Hand Interaction Profile: {left_name}")
            else:
                print("Left Hand Interaction Profile: NONE (no profile bound)")
            
            if right_profile.interaction_profile != xr.NULL_PATH:
                right_name = xr.path_to_string(self.instance, right_profile.interaction_profile)
                print(f"Right Hand Interaction Profile: {right_name}")
            else:
                print("Right Hand Interaction Profile: NONE (no profile bound)")
        except Exception as e:
            print(f"Could not get interaction profiles: {e}")

    def setup_spaces(self):
        self.ref_space = xr.create_reference_space(
            self.session,
            xr.ReferenceSpaceCreateInfo(
                reference_space_type=xr.ReferenceSpaceType.VIEW,
                pose_in_reference_space=xr.Posef(),
            )
        )
        
        left_hand = xr.string_to_path(self.instance, "/user/hand/left")
        right_hand = xr.string_to_path(self.instance, "/user/hand/right")
        
        self.left_aim_space = xr.create_action_space(self.session, xr.ActionSpaceCreateInfo(action=self.action_aim_pose, subaction_path=left_hand))
        self.right_aim_space = xr.create_action_space(self.session, xr.ActionSpaceCreateInfo(action=self.action_aim_pose, subaction_path=right_hand))
        self.left_grip_space = xr.create_action_space(self.session, xr.ActionSpaceCreateInfo(action=self.action_grip_pose, subaction_path=left_hand))
        self.right_grip_space = xr.create_action_space(self.session, xr.ActionSpaceCreateInfo(action=self.action_grip_pose, subaction_path=right_hand))

    def sync_actions(self):
        active_action_set = xr.ActiveActionSet(action_set=self.action_set, subaction_path=xr.NULL_PATH)
        xr.sync_actions(self.session, xr.ActionsSyncInfo(active_action_sets=[active_action_set]))

    def print_pose(self, name, space, display_time):
        velocity = xr.SpaceVelocity(type=xr.StructureType.SPACE_VELOCITY)
        location = xr.SpaceLocation(
            type=xr.StructureType.SPACE_LOCATION,
            next=ctypes.cast(ctypes.byref(velocity), ctypes.c_void_p)
        )
        
        result = self.xrLocateSpace(space, self.ref_space, display_time, ctypes.byref(location))
        
        if result != xr.Result.SUCCESS:
            print(f"{name} Locate Failed: {result}")
            return

        if location.location_flags & xr.SPACE_LOCATION_POSITION_VALID_BIT:
            pos = location.pose.position
            rot = location.pose.orientation
            print(f"{name} Pos: ({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f}) "
                  f"Rot: ({rot.x:.3f}, {rot.y:.3f}, {rot.z:.3f}, {rot.w:.3f})")
            
            if velocity.velocity_flags & xr.SPACE_VELOCITY_LINEAR_VALID_BIT:
                lin_vel = velocity.linear_velocity
                print(f"    Lin Vel: ({lin_vel.x:.3f}, {lin_vel.y:.3f}, {lin_vel.z:.3f})")
            
    def get_pose_data(self, space, display_time):
        velocity = xr.SpaceVelocity(type=xr.StructureType.SPACE_VELOCITY)
        location = xr.SpaceLocation(
            type=xr.StructureType.SPACE_LOCATION,
            next=ctypes.cast(ctypes.byref(velocity), ctypes.c_void_p)
        )
        
        result = self.xrLocateSpace(space, self.ref_space, display_time, ctypes.byref(location))
        
        if result != xr.Result.SUCCESS:
            return None

        data = {}
        if location.location_flags & xr.SPACE_LOCATION_POSITION_VALID_BIT:
            data['position'] = location.pose.position
            data['orientation'] = location.pose.orientation
        
        # We could also return velocity if needed, but let's stick to pose for now or add it to the dict
        # The ROS interface expects 'position' and 'orientation' keys with objects having x,y,z attributes
        
        return data if data else None

    def get_input_data(self, hand="left", debug=False):
        """
        Get button and analog input data for specified hand.
        Returns a dict compatible with ros_interface._to_ros_joy()
        """
        hand_path = self.left_hand_path if hand == "left" else self.right_hand_path
        
        data = {}
        
        # Get Trigger value (Float)
        try:
            trigger_state = xr.get_action_state_float(
                self.session,
                xr.ActionStateGetInfo(action=self.action_trigger, subaction_path=hand_path)
            )
            if debug:
                print(f"  {hand} Trigger: active={trigger_state.is_active}, value={trigger_state.current_state}")
            if trigger_state.is_active:
                data['trigger'] = trigger_state.current_state
            else:
                data['trigger'] = 0.0
        except Exception as e:
            if debug:
                print(f"  {hand} Trigger ERROR: {e}")
            data['trigger'] = 0.0
        
        # Get Squeeze value (Float)
        try:
            squeeze_state = xr.get_action_state_float(
                self.session,
                xr.ActionStateGetInfo(action=self.action_squeeze, subaction_path=hand_path)
            )
            if debug:
                print(f"  {hand} Squeeze: active={squeeze_state.is_active}, value={squeeze_state.current_state}")
            if squeeze_state.is_active:
                data['squeeze'] = squeeze_state.current_state
            else:
                data['squeeze'] = 0.0
        except Exception as e:
            if debug:
                print(f"  {hand} Squeeze ERROR: {e}")
            data['squeeze'] = 0.0
        
        # Get Thumbstick (Vector2f)
        try:
            thumbstick_state = xr.get_action_state_vector2f(
                self.session,
                xr.ActionStateGetInfo(action=self.action_thumbstick, subaction_path=hand_path)
            )
            if debug:
                print(f"  {hand} Thumbstick: active={thumbstick_state.is_active}, x={thumbstick_state.current_state.x}, y={thumbstick_state.current_state.y}")
            if thumbstick_state.is_active:
                data['thumbstick_x'] = thumbstick_state.current_state.x
                data['thumbstick_y'] = thumbstick_state.current_state.y
            else:
                data['thumbstick_x'] = 0.0
                data['thumbstick_y'] = 0.0
        except Exception as e:
            if debug:
                print(f"  {hand} Thumbstick ERROR: {e}")
            data['thumbstick_x'] = 0.0
            data['thumbstick_y'] = 0.0
        
        # Get Thumbstick Click (Boolean)
        try:
            thumbstick_click_state = xr.get_action_state_boolean(
                self.session,
                xr.ActionStateGetInfo(action=self.action_thumbstick_click, subaction_path=hand_path)
            )
            if debug:
                print(f"  {hand} StickClick: active={thumbstick_click_state.is_active}, value={thumbstick_click_state.current_state}")
            if thumbstick_click_state.is_active:
                data['thumbstick_click'] = thumbstick_click_state.current_state
            else:
                data['thumbstick_click'] = False
        except Exception as e:
            if debug:
                print(f"  {hand} StickClick ERROR: {e}")
            data['thumbstick_click'] = False
        
        # Get Button A/X (depends on hand)
        if hand == "right":
            # A and B buttons on right controller
            try:
                a_state = xr.get_action_state_boolean(
                    self.session,
                    xr.ActionStateGetInfo(action=self.action_button_a, subaction_path=hand_path)
                )
                if debug:
                    print(f"  {hand} Button A: active={a_state.is_active}, value={a_state.current_state}")
                data['button_a_x'] = a_state.current_state if a_state.is_active else False
            except Exception as e:
                if debug:
                    print(f"  {hand} Button A ERROR: {e}")
                data['button_a_x'] = False
            
            try:
                b_state = xr.get_action_state_boolean(
                    self.session,
                    xr.ActionStateGetInfo(action=self.action_button_b, subaction_path=hand_path)
                )
                if debug:
                    print(f"  {hand} Button B: active={b_state.is_active}, value={b_state.current_state}")
                data['button_b_y'] = b_state.current_state if b_state.is_active else False
            except Exception as e:
                if debug:
                    print(f"  {hand} Button B ERROR: {e}")
                data['button_b_y'] = False
            
            data['menu'] = False  # Menu button is only on left controller
        else:
            # X and Y buttons on left controller
            try:
                x_state = xr.get_action_state_boolean(
                    self.session,
                    xr.ActionStateGetInfo(action=self.action_button_x, subaction_path=hand_path)
                )
                if debug:
                    print(f"  {hand} Button X: active={x_state.is_active}, value={x_state.current_state}")
                data['button_a_x'] = x_state.current_state if x_state.is_active else False
            except Exception as e:
                if debug:
                    print(f"  {hand} Button X ERROR: {e}")
                data['button_a_x'] = False
            
            try:
                y_state = xr.get_action_state_boolean(
                    self.session,
                    xr.ActionStateGetInfo(action=self.action_button_y, subaction_path=hand_path)
                )
                if debug:
                    print(f"  {hand} Button Y: active={y_state.is_active}, value={y_state.current_state}")
                data['button_b_y'] = y_state.current_state if y_state.is_active else False
            except Exception as e:
                if debug:
                    print(f"  {hand} Button Y ERROR: {e}")
                data['button_b_y'] = False
            
            # Menu button on left controller
            try:
                menu_state = xr.get_action_state_boolean(
                    self.session,
                    xr.ActionStateGetInfo(action=self.action_menu, subaction_path=hand_path)
                )
                if debug:
                    print(f"  {hand} Menu: active={menu_state.is_active}, value={menu_state.current_state}")
                data['menu'] = menu_state.current_state if menu_state.is_active else False
            except Exception as e:
                if debug:
                    print(f"  {hand} Menu ERROR: {e}")
                data['menu'] = False
        
        return data

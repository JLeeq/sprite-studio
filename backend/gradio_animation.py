"""애니메이션 함수들"""

import os
import zipfile
from PIL import Image
from .pixel_character_generator import generate_pixel_character_interface
from .game_asset_generator import get_global_generator

def create_sprite_animation_zip(image_paths, action_type):
    """Create a ZIP file containing all generated sprite animation images"""
    if not image_paths or len(image_paths) == 0:
        return None, "❌ No images to download. Please generate sprites first."
    
    try:
        # Filter out None values and check if paths exist
        valid_paths = []
        for img_path in image_paths:
            if img_path:
                # Handle both string paths and Gradio file objects
                if isinstance(img_path, str):
                    path = img_path
                elif hasattr(img_path, 'name'):
                    path = img_path.name
                else:
                    path = str(img_path)
                
                if os.path.exists(path):
                    valid_paths.append(path)
        
        if len(valid_paths) == 0:
            return None, "❌ No valid images found. Please generate sprites first."
        
        # Create a temporary directory for the ZIP file
        temp_dir = os.path.join(os.getenv("OUTPUT_DIR", "data/output"), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create ZIP file name with timestamp
        timestamp = int(time.time())
        zip_filename = f"{action_type}_sprites_{timestamp}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        # Create ZIP file and add all images
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, img_path in enumerate(valid_paths):
                # Add frame number prefix for better organization
                if i == 0:
                    frame_name = "00_original.png"
                elif i == len(valid_paths) - 1:
                    frame_name = f"{i:02d}_combined_sheet.png"
                else:
                    frame_name = f"{i:02d}_frame_{i}.png"
                
                # Add file to ZIP with organized name
                zipf.write(img_path, frame_name)
        
        print(f"✅ ZIP file created: {zip_path} ({len(valid_paths)} images)")
        return zip_path, f"✅ ZIP file created successfully! ({len(valid_paths)} images)"
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error creating ZIP file: {error_msg}")
        print(traceback.format_exc())
        return None, f"❌ Error creating ZIP file: {error_msg}"

def generate_pixel_character(description, character_reference_image=None, item_reference_image=None):
    """Pixel character generation interface function"""
    # Input validation
    if not description or not description.strip():
        return "❌ Please enter a character description. e.g., 'cute pink-haired person', 'scary blue dragon'", None
    
    try:
        # Generate pixel character
        status, img_path = generate_pixel_character_interface(description, character_reference_image, item_reference_image)
        return status, img_path
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Pixel character generation error: {error_msg}")
        print(traceback.format_exc())
        return f"❌ Error during generation: {error_msg}\nPlease try again.", None

def generate_sprite_animation(reference_image, action_type):
    """Generate sprite animation using Gemini - 6 frames (attack, jump, or walk)"""
    # Input validation
    if reference_image is None:
        return [], "❌ Please upload a character reference image first."
    
    if action_type not in ["attack", "jump", "walk"]:
        return [], "❌ Please select a valid animation type (attack, jump, or walk)."
    
    try:
        # Get file path from Gradio upload object
        if hasattr(reference_image, 'name'):
            image_path = reference_image.name
        else:
            image_path = reference_image
        
        print(f"🔍 Generating 6-frame {action_type} animation with Gemini...")
        print(f"Image path: {image_path}")
        
        # Load the reference image
        reference_img = Image.open(image_path)
        
        # Define frame prompts based on action type
        if action_type == "attack":
            frame_prompts = {
                "frame1_idle": """Generate the character according to the following description.

character facing RIGHT, idle ready stance: head slightly turned right, calm eyes forward, torso upright and relaxed, right hand holding weapon low at side, left arm resting naturally, feet shoulder-width apart, faint small glow at weapon tip, transparent background. 
Weapon consistency rule: The weapon must remain EXACTLY the same as in the reference image — same shape, size, color, and design details. Do NOT change or redesign the weapon in any way. The character must hold the same weapon throughout all frames.
CRITICAL: Character must face RIGHT direction.
Art Style Rule:
All generated frames must follow the exact visual style shown in the reference character.  
If the reference uses pixel rendering, continue that pixel look.  
If the reference is drawn in another style, the output must preserve that same aesthetic without converting it to pixel form.  
Do not alter, simplify, or reinterpret the art style.

Weapon Consistency:
The weapon must remain completely identical to the one in the reference — same appearance, color palette, silhouette, and proportions.  
No edits or new variations are allowed across any frame.

Pose & Center Alignment:
Each frame must keep the character anchored to the same center point so that animation remains stable.  
Limbs must bend with natural anatomy — elbows and knees should curve smoothly instead of forming stiff, straight mechanical angles.

Hair Movement Rule (if the character has hair):
During attack sequences, hair should flow dynamically toward the LEFT, giving a sense of explosive motion and high impact.

Facial Expression Variation:
The eyes and facial expression should shift subtly or dramatically depending on the frame’s purpose, enhancing emotion and motion.

The character stands facing RIGHT in a poised battle-ready stance.  
The head is angled slightly toward the right with calm, focused eyes.  
Torso remains upright and relaxed.  
Right hand grips the original weapon lowered near the side, while the left arm rests naturally.  
Feet are set shoulder-width apart, stable and grounded.  
A faint, subtle gleam appears at the edge of the weapon.

If the character has hair, it should drift gently toward the LEFT, as if touched by an early stirring of energy.  
Expression: composed but alert.

Transparent background.
Keep the weapon identical to the reference in every detail.
Preserve the same art style and maintain consistent center alignment with natural limb bends.
""",
                
                "frame2_chargeup": """Generate the character according to the following description.

character facing RIGHT, charge-up pose: head focused on weapon tip, torso leaning slightly back, right arm lifting weapon upward with elbow bent, left hand balancing or supporting, feet stable with weight shifted backward, small glowing orb forming at weapon tip with spark particles, transparent background. CRITICAL: Character must face RIGHT direction.

Facing RIGHT, the character begins gathering power.  
The torso leans slightly backward, and the head focuses sharply on the weapon’s tip.  
The right arm lifts the weapon upward with a bent elbow while the left hand provides balance.  
A bright sphere of energy starts forming at the weapon’s point, with small radiant sparks circling it.

If the character has hair, it should sweep LEFT more strongly, reacting to the intensified energy.  
Expression: determination rising, eyes narrowed with concentration.

Transparent background.
Same weapon, same art style, same center point, natural joints.
""",
                
                "frame3_aim": """Generate the character according to the following description.

character facing RIGHT, pre-attack aiming pose: head locked forward with fierce focus, torso leaning slightly forward, right arm extending weapon forward, left arm balancing near chest, front foot pressing down, energy orb at weapon tip growing brighter with small electric arcs, transparent background. CRITICAL: Character must face RIGHT direction.
The character keeps facing RIGHT, leaning slightly forward.  
Right arm extends the weapon forward as the left arm stabilizes near the chest.  
The energy sphere expands, pulsing with streaks of electricity.  
Lower body pushes into a firm stance, ready to strike.

Hair (if any) blows LEFT in a sharper arc, emphasizing forward focus.  
Expression: fierce and locked onto the target.

Transparent background.
Preserve weapon identity, art style, center, and natural joint bending.
""",
                
                "frame4_lunge": """Generate the character according to the following description.

character facing RIGHT, lunge attack-prep pose: head determined and looking forward, torso thrust forward, right arm fully extended pushing weapon ahead, left arm stretched back for balance, front leg stepping forward bearing weight, weapon tip glowing at peak intensity with bright aura and motion trails, transparent background. CRITICAL: Character must face RIGHT direction, same as other frames.

The character thrusts aggressively to the RIGHT.  
Torso surges forward, and the weapon is driven outward with full extension.  
Left arm reaches backward for balance.  
Front leg moves decisively forward, absorbing momentum.  
Energy at the weapon tip radiates in a vivid, concentrated glow with motion streaks.

Hair streams LEFT dramatically, showing intense acceleration.  
Expression: eyes wide with aggressive intent.

Transparent background.
Follow all consistency rules. 
""",              
                "frame5_impact": """Generate the character according to the following description.

character facing RIGHT, attack impact pose: head focused forward, torso leaning into the strike, right arm extended holding weapon, left arm offset for balance, front foot planted, massive energy burst from weapon tip with bright white core and colored shockwave rings, spark particles around, transparent background. CRITICAL: Character must face RIGHT direction.

The character delivers a full-force impact toward the RIGHT.  
Torso leans deeply into the strike, and the weapon extends forward.  
A powerful explosion of light bursts from the weapon’s tip — brilliant core, expanding shock rings, scattered sparks.

Hair blows LEFT in a violent, high-speed motion.  
Expression: intense, focused, almost explosive.

Transparent background.
Same weapon, same style, same pivot, natural limb curvature.    
""",          
                "frame6_aftershock": """Generate the character according to the following description.

character facing RIGHT, aftershock dissipate pose: head slightly lowered but still facing right, expression calm but focused, torso slightly leaned forward holding weapon extended after impact, both hands steady but relaxed, feet fixed in same stance as impact frame. 
Bright energy from weapon tip has just faded — residual pink light rings expand outward, fading into transparency with soft glow, small spark particles dispersing and disappearing, faint motion blur suggesting energy release completion. 
Transparent background. CRITICAL: Character must face RIGHT direction, maintain same pivot and proportions as previous frames.
The character remains facing RIGHT as the energy dissipates.  
Torso stays slightly forward, arms steady but relaxing after the impact.  
Soft fading light rings expand where the strike occurred.  
Tiny spark fragments drift outward and disappear.

Hair (if present) settles while still flowing slightly LEFT as the movement slows.  
Expression: calm, controlled, returning to focus.

Transparent background.
Maintain all consistency rules, center alignment, original weapon, and art style.
"""
            }
        elif action_type == "jump":
            frame_prompts = {
                "frame1_prepare": """Generate the character according to the following description.

character facing RIGHT, jump preparation pose: head slightly tilted down, eyes forward, torso slightly crouched, knees bent, right hand holding the same weapon low near waist, left arm slightly back for balance, feet shoulder-width pressing down as if gathering strength to jump. 
Transparent background. Maintain SAME weapon design/shape/size/colors as reference; 1:1 head-to-body, two arms two legs, SAME pivot as other actions. CRITICAL: Character must face RIGHT direction.

The character faces RIGHT in a lowered stance, preparing to jump.  
The head dips slightly with eyes focused forward.  
Torso leans subtly downward, knees bent, weight gathered in the legs.  
Right hand holds the same weapon near the waist at a neutral angle, while the left arm shifts backward for balance.  
Feet press firmly into the ground, signaling that strength is being stored.

If the character has hair, it should drift LEFT with a gentle, anticipatory motion.  
Expression: steady, concentrated.

Transparent background.
Maintain identical art style, same center alignment, original weapon design, and naturally curved elbows and knees.
""",

                "frame2_launch": """Generate the character according to the following description.

character facing RIGHT, jump launch pose: head oriented slightly upward, torso pushing upward dynamically, both legs extending from crouch, right arm pulling weapon slightly backward for momentum, left arm forward balancing, small dust particles under feet. 
Transparent background. SAME weapon & proportions & pivot. CRITICAL: Character must face RIGHT direction.

Facing RIGHT, the character forcefully pushes upward, leaving the ground.  
The torso drives upward with momentum, legs extending from the crouched position.  
Right arm pulls the weapon slightly behind the body, while the left arm moves forward for counterbalance.  
Dust fragments and a small burst of debris appear beneath the feet, showing lift-off.

Hair (if any) lifts and sweeps LEFT more noticeably due to the upward motion.  
Expression: focused and determined, eyes widening slightly.

Transparent background.
Keep the same art style, same pivot position, same weapon, and organic limb bending.
""",

                "frame3_air_rise": """Create the character according to the description below.

character facing RIGHT, mid-air rising pose: head slightly up, torso extended, legs tucked slightly toward body, right arm holding weapon diagonally across the front, left arm extended backward for balance, faint motion lines beneath character. 
Transparent background. SAME weapon, SAME pivot, 1:1 chibi. CRITICAL: Character must face RIGHT direction.

The character ascends through the air while still facing RIGHT.  
Torso angles upward lightly as both legs tuck in toward the body.  
Right arm holds the weapon diagonally across the front of the torso, while the left arm extends backward for aerial balance.  
Subtle motion lines appear beneath the character to show upward movement.

If the character has hair, it should trail LEFT with a freer, wider curve.  
Expression: slightly excited or fierce, showing dynamic energy.

Transparent background.
Follow same art style, pivot, weapon identity, and natural joint motion.
""",

                "frame4_air_peak": """Create the character according to the description below.
character facing RIGHT, jump apex pose: head level, torso upright, both legs lightly bent as if floating at the top, right arm steady holding weapon horizontally, left arm relaxed near side, subtle floating particles around. 
Transparent background. SAME weapon & proportions & pivot. CRITICAL: Character must face RIGHT direction.

The character reaches the top of the jump, still oriented RIGHT.  
Body floats lightly—head level, torso straightened.  
Both legs bend softly as if briefly suspended in midair.  
Right arm steadies the weapon horizontally or at a relaxed diagonal, while the left arm rests near the side.  
Small ambient particles or sparkles can appear around the character to emphasize the moment of weightlessness.

Hair (if present) flows LEFT, but with a softer arc compared to earlier frames.  
Expression: calm focus, eyes slightly softened.

Transparent background.
Art style, center alignment, weapon fidelity, and natural joints must be maintained.
""",

                "frame5_air_fall": """Create the character according to the description below.

character facing RIGHT, descending pose: head angled slightly downward, torso leaning a bit forward, right arm and weapon angled downward preparing to land, left arm behind for balance, legs extended downward with knees slightly bent, thin downward motion trails. 
Transparent background. SAME weapon & pivot. CRITICAL: Character must face RIGHT direction.

Still facing RIGHT, the character begins descending.  
Torso leans slightly forward as gravity takes effect.  
Legs extend downward with light bend in the knees, preparing for the landing.  
Right hand angles the weapon downward, anticipating contact with the ground.  
Left arm shifts behind the body for midair stabilization.  
Thin downward motion trails emphasize the falling movement.

If the character has hair, it continues flowing LEFT but begins to settle gradually.  
Expression: alert and ready, eyes narrowing again.

Transparent background.
Maintain art style, weapon identity, pivot point, and smooth elbow/knee curvature.
""",

                "frame6_land": """Create the character according to the description below.

character facing RIGHT, landing impact pose: head slightly forward, torso lowered with deep knee bend, front foot planted, back foot heel lifted, right hand gripping weapon forward for stability, small dust clouds under feet and a tiny shock ring. 
Transparent background. Maintain SAME weapon (no redesign), 1:1 ratio, two arms two legs, SAME pivot as previous frames. CRITICAL: Character must face RIGHT direction.


The character lands firmly while still positioned to the RIGHT.  
Torso compresses downward with a deep bend in the knees.  
Front foot plants solidly while the back heel lifts slightly from the force.  
Right hand braces the weapon forward for stability, and the left arm supports balance near the torso.  
A small shock ring and dust burst appear beneath the feet to illustrate the impact.

Hair (if any) sweeps LEFT one last time, then begins settling back toward its natural shape.  
Expression: intense but recovering, eyes steady and focused.

Transparent background.
Preserve the exact art style, the same weapon structure, identical pivot alignment, and naturally curved limbs.
"""
            }
        else:  # walk
            frame_prompts = {
                "frame1_walk": """Create the character according to the description below.

character facing RIGHT, relaxed WALK pose: front foot stepping forward, back heel lifted slightly. Arms swing naturally (front arm back, rear arm forward). Expression calm and focused. Maintain exact outfit, weapon, proportions from reference. Transparent background. CRITICAL: Character must face RIGHT direction.""",

                "frame2_run": """Create the character according to the description below.

character facing RIGHT, energetic RUN pose: torso leaning forward, front knee lifted high, rear leg extended behind. Arms pumping with energy, small motion lines trailing. Expression determined. Maintain EXACT appearance from reference. Transparent background. CRITICAL: Character faces RIGHT.""",

                "frame3_walk": """Create the character according to the description below.

character facing RIGHT, second WALK pose: opposite foot forward (compared to frame1), gentle torso sway, arms continuing natural swing. Outfit/weapon identical to reference. Transparent background. CRITICAL: Character faces RIGHT.""",

                "frame4_run": """Create the character according to the description below.

character facing RIGHT, RUN pose mid-stride: both feet off ground, front leg extended, rear leg bent. Arms reach farther for speed, motion streaks behind limbs. Same outfit/weapon/proportions as reference. Transparent background. CRITICAL: Character faces RIGHT.""",

                "frame5_walk": """Create the character according to the description below.

character facing RIGHT, WALK pose resetting into rhythmic loop: feet closer together mid-transition, slight bounce in torso, arms nearly vertical. Maintain identical appearance. Transparent background. CRITICAL: Character faces RIGHT.""",

                "frame6_run": """Create the character according to the description below.

character facing RIGHT, RUN finishing pose: front foot about to land, rear leg tucked under, arms angled strongly, motion lines emphasizing speed. KEEP outfit/weapon identical. Transparent background. CRITICAL: Character faces RIGHT."""
            }
        
        # Get the global generator to use Gemini client
        generator = get_global_generator()
        
        # Generate all 6 frames
        generated_images = []
        output_dir = os.path.join(os.getenv("OUTPUT_DIR", "data/output"), "characters")
        os.makedirs(output_dir, exist_ok=True)
        
        # Add original reference image as first frame
        generated_images.append(image_path)
        print(f"✅ Original character added as first frame: {image_path}")
        
        for frame_name, prompt in frame_prompts.items():
            print(f"🎨 Generating {frame_name}...")
            
            try:
                # Generate image using Gemini
                content = [prompt, reference_img]
                response = generator.image_gen_client.models.generate_content(
                    model=generator.image_gen_model_name,
                    contents=content
                )
                
                # Save the generated image
                timestamp = int(time.time())
                output_path = os.path.join(output_dir, f"{action_type}_{frame_name}_{timestamp}.png")
                
                # Save image from Gemini response
                saved_image = generator.save_image(response, output_path)
                
                if saved_image:
                    generated_images.append(output_path)
                    print(f"✅ {frame_name} saved: {output_path}")
                else:
                    print(f"⚠️ Failed to save {frame_name}")
                
                # Longer delay between requests to avoid rate limiting
                time.sleep(3)
                
            except Exception as frame_error:
                error_msg = str(frame_error)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    print(f"⚠️ {frame_name} failed due to quota limit")
                    return [], "❌ Gemini API 할당량이 소진되었습니다. 잠시 후 다시 시도해주세요. (429 RESOURCE_EXHAUSTED)"
                else:
                    print(f"⚠️ {frame_name} failed: {error_msg}")
                    # Continue with other frames even if one fails
        
        if len(generated_images) == 7:  # Original + 6 generated frames
            # Create combined sprite sheet using numpy.hstack
            print("🎨 Creating combined sprite sheet...")
            try:
                # Load all images and convert to RGB if needed
                images = []
                for i, img_path in enumerate(generated_images):
                    print(f"Loading image {i+1}: {img_path}")
                    img = Image.open(img_path)
                    # Convert to RGB if image has transparency (RGBA)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create white background for transparent images
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
                    print(f"Image {i+1} loaded: {img.size}, mode: {img.mode}")
                
                # Resize all images to the same height (use the first image's height)
                base_height = images[0].height
                print(f"Base height: {base_height}")
                resized_images = []
                for i, img in enumerate(images):
                    # Calculate new width maintaining aspect ratio
                    aspect_ratio = img.width / img.height
                    new_width = int(base_height * aspect_ratio)
                    resized_img = img.resize((new_width, base_height), Image.Resampling.LANCZOS)
                    resized_images.append(resized_img)
                    print(f"Resized image {i+1}: {resized_img.size}")
                
                # Convert to numpy arrays and stack horizontally
                numpy_images = [np.array(img) for img in resized_images]
                print(f"Converting to numpy arrays, shapes: {[arr.shape for arr in numpy_images]}")
                combined_array = np.hstack(numpy_images)
                print(f"Combined array shape: {combined_array.shape}")
                
                # Convert back to PIL Image
                combined_image = Image.fromarray(combined_array)
                
                # Save combined image
                timestamp = int(time.time())
                combined_path = os.path.join(output_dir, f"{action_type}_combined_{timestamp}.png")
                combined_image.save(combined_path, 'PNG')
                
                # Add combined image to the list
                generated_images.append(combined_path)
                print(f"✅ Combined sprite sheet saved: {combined_path}")
                
                action_emoji = "⚔️" if action_type == "attack" else "🦘"
                return generated_images, f"✅ Successfully generated 8 frames (Original + 6 {action_type} frames + Combined sprite sheet) with Gemini! 🎮{action_emoji}"
                
            except Exception as combine_error:
                import traceback
                print(f"⚠️ Failed to create combined sprite sheet: {combine_error}")
                print(f"Full traceback: {traceback.format_exc()}")
                action_emoji = "⚔️" if action_type == "attack" else "🦘"
                return generated_images, f"✅ Generated 7 frames (Original + 6 {action_type} frames) with Gemini! (Combined sheet failed: {str(combine_error)}) 🎮{action_emoji}"
                
        elif len(generated_images) > 1:  # At least original + some generated frames
            generated_count = len(generated_images) - 1  # Subtract original
            return generated_images, f"⚠️ Generated {generated_count}/6 {action_type} frames. Some frames failed."
        else:
            return [], "❌ Failed to generate any frames."
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"{action_type} animation generation error: {error_msg}")
        print(traceback.format_exc())
        return [], f"❌ Error during generation: {error_msg}\nPlease try again."

def generate_dead_animation(reference_image):
    """Generate dead animation using Gemini - 5 frames"""
    # Input validation
    if reference_image is None:
        return [], "❌ Please upload a character reference image first."
    
    try:
        # Get file path from Gradio upload object
        if hasattr(reference_image, 'name'):
            image_path = reference_image.name
        else:
            image_path = reference_image
        
        print("🔍 Generating 5-frame dead animation with Gemini...")
        print(f"Image path: {image_path}")
        
        # Load the reference image
        reference_img = Image.open(image_path)
        
        # Define 5 frame prompts for dead animation
        frame_prompts_dead = {
            "frame1_hit_recoil": """Create the character according to the description below.

Character facing RIGHT at the exact moment a heavy blow lands.  
The head is jerked sharply BACK and slightly LEFT relative to the torso, with eyes opened wide from shock.  
Eyebrows lift dramatically and the mouth forms a brief gasp.  
Upper body bends backward around 15 degrees, causing one leg to slip out of balance.  
Both arms swing erratically from the sudden force, and the weapon trembles loosely but remains held.  
Facial expression must convey immediate pain and surprise — never calm.

Transparent background.
Weapon must remain identical in design, color, and scale.
Character orientation must remain RIGHT-facing at all times.
""",

            "frame2_knockback_airborne": """Generate the character based on the details below.


Facing RIGHT, the character has been hurled into the air by the impact.  
Head tilts even farther back and LEFT compared to the previous frame, eyes half-lidded as awareness begins to slip.  
Mouth hangs partially open as if exhaling mid-flight.  
The torso rotates backward around 45 degrees, legs rising higher toward the RIGHT side.  
Arms spread uncontrollably due to inertia.

Expression should appear hazy and fading.

Transparent background.
Keep the same pivot point and the same weapon exactly as in the reference.
Character must still be directed toward the RIGHT.
""",

            "frame3_mid_flip": """Generate the character based on the details below.


The character remains RIGHT-facing while rotating through mid-air, somewhere between being horizontal and upside-down.  
Head stays LEFT of the legs and lowers relative to the torso — roughly a 75-degree rotation from an upright stance.  
Torso angles diagonally with the chest turning upward-left, legs arcing slightly higher toward the RIGHT.  
Both arms extend outward along the rotational path, guided by the spin’s momentum.  
Eyes are partially closed and the mouth tightens subtly, signaling weakening consciousness.  
The weapon follows the rotation, angled behind the character but still firmly held.  
Rotation direction must be CLOCKWISE with gravity pulling downward.

Transparent background.
Maintain matching weapon style, pivot position, and character proportions.
""",

            "frame4_fall_transition": """Generate the character based on the details below.
The character, still facing RIGHT, continues rotating while falling.  
Head remains on the LEFT side of the body but is now lower, close to a horizontal alignment — approximately a 140-degree shift from upright.  
Torso arches back slightly as the fall accelerates, with the legs still elevated toward the RIGHT.  
Arms and weapon trail naturally downward, pulled by both momentum and gravity.  
Expression appears drained, eyes nearly shut, the whole body showing looseness and loss of control.  
Rotation remains CLOCKWISE — the head must always stay LEFT of the legs.

Transparent background.
Same weapon design, pivot consistency, and matching proportions are required.
""",

            "frame5_rest": """Generate the character based on the details below.

Character facing RIGHT and lying collapsed on the ground, completely motionless.  
Head rests to the LEFT side of the torso, turned sideways.  
Eyes fully shut; mouth slightly open; expression empty and lifeless.  
Arms and legs fall naturally to the ground, heavy and unresponsive.  
The weapon lies near the hand, with no light or energy remaining.

The scene must show absence of life — no serenity or smile.

Transparent background.
Weapon, pivot alignment, and overall proportions must remain consistent with previous frames.

"""
        }
        
        # Get the global generator to use Gemini client
        generator = get_global_generator()
        
        # Generate all 5 frames
        generated_images = []
        output_dir = os.path.join(os.getenv("OUTPUT_DIR", "data/output"), "characters")
        os.makedirs(output_dir, exist_ok=True)
        
        # Add original reference image as first frame
        generated_images.append(image_path)
        print(f"✅ Original character added as first frame: {image_path}")
        
        for frame_name, prompt in frame_prompts_dead.items():
            print(f"🎨 Generating {frame_name}...")
            
            try:
                # Generate image using Gemini
                content = [prompt, reference_img]
                response = generator.image_gen_client.models.generate_content(
                    model=generator.image_gen_model_name,
                    contents=content
                )
                
                # Save the generated image
                timestamp = int(time.time())
                output_path = os.path.join(output_dir, f"dead_{frame_name}_{timestamp}.png")
                
                # Save image from Gemini response
                saved_image = generator.save_image(response, output_path)
                
                if saved_image:
                    generated_images.append(output_path)
                    print(f"✅ {frame_name} saved: {output_path}")
                else:
                    print(f"⚠️ Failed to save {frame_name}")
                
                # Longer delay between requests to avoid rate limiting
                time.sleep(3)
                
            except Exception as frame_error:
                error_msg = str(frame_error)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    print(f"⚠️ {frame_name} failed due to quota limit")
                    return [], "❌ Gemini API 할당량이 소진되었습니다. 잠시 후 다시 시도해주세요. (429 RESOURCE_EXHAUSTED)"
                else:
                    print(f"⚠️ {frame_name} failed: {error_msg}")
                    # Continue with other frames even if one fails
        
        if len(generated_images) == 6:  # Original + 5 generated frames
            # Create combined sprite sheet using numpy.hstack
            print("🎨 Creating combined sprite sheet...")
            try:
                # Load all images and convert to RGB if needed
                images = []
                for i, img_path in enumerate(generated_images):
                    print(f"Loading image {i+1}: {img_path}")
                    img = Image.open(img_path)
                    # Convert to RGB if image has transparency (RGBA)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create white background for transparent images
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
                    print(f"Image {i+1} loaded: {img.size}, mode: {img.mode}")
                
                # Resize all images to the same height (use the first image's height)
                base_height = images[0].height
                print(f"Base height: {base_height}")
                resized_images = []
                for i, img in enumerate(images):
                    # Calculate new width maintaining aspect ratio
                    aspect_ratio = img.width / img.height
                    new_width = int(base_height * aspect_ratio)
                    resized_img = img.resize((new_width, base_height), Image.Resampling.LANCZOS)
                    resized_images.append(resized_img)
                    print(f"Resized image {i+1}: {resized_img.size}")
                
                # Convert to numpy arrays and stack horizontally
                numpy_images = [np.array(img) for img in resized_images]
                print(f"Converting to numpy arrays, shapes: {[arr.shape for arr in numpy_images]}")
                combined_array = np.hstack(numpy_images)
                print(f"Combined array shape: {combined_array.shape}")
                
                # Convert back to PIL Image
                combined_image = Image.fromarray(combined_array)
                
                # Save combined image
                timestamp = int(time.time())
                combined_path = os.path.join(output_dir, f"dead_combined_{timestamp}.png")
                combined_image.save(combined_path, 'PNG')
                
                # Add combined image to the list
                generated_images.append(combined_path)
                print(f"✅ Combined sprite sheet saved: {combined_path}")
                
                return generated_images, f"✅ Successfully generated 7 frames (Original + 5 dead frames + Combined sprite sheet) with Gemini! 🎮💀"
                
            except Exception as combine_error:
                import traceback
                print(f"⚠️ Failed to create combined sprite sheet: {combine_error}")
                print(f"Full traceback: {traceback.format_exc()}")
                return generated_images, f"✅ Generated 6 frames (Original + 5 dead frames) with Gemini! (Combined sheet failed: {str(combine_error)}) 🎮💀"
                
        elif len(generated_images) > 1:  # At least original + some generated frames
            generated_count = len(generated_images) - 1  # Subtract original
            return generated_images, f"⚠️ Generated {generated_count}/5 dead frames. Some frames failed."
        else:
            return [], "❌ Failed to generate any frames."
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Dead animation generation error: {error_msg}")
        print(traceback.format_exc())
        return [], f"❌ Error during generation: {error_msg}\nPlease try again."

def generate_universal_animation(reference_image, action_type):
    """Route animation generation based on the selected action type."""
    normalized_type = (action_type or "").strip().lower()
    if normalized_type == "dead":
        return generate_dead_animation(reference_image)
    return generate_sprite_animation(reference_image, normalized_type or "attack")

def update_animation_info(action_type):
    """Update animation info based on selected action type"""
    # 텍스트 설명을 숨기기 위해 빈 문자열 반환
    return "", ""

def save_config_interface(config_name, art_style, mood, color_palette, 
                         character_style, line_style, composition, additional_notes):
    """설정을 저장하는 인터페이스 함수"""

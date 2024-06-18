import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import base64
import io
from PIL import Image, PngImagePlugin
import datetime
import aiohttp
import random
import sqlite3
import asyncio
import glob
import re

# Initialize Discord bot with intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
intents.reactions = True
intents.emojis_and_stickers = True
intents.integrations = True
intents.webhooks = True
intents.invites = False
intents.voice_states = False
intents.presences = True
intents.typing = False

bot = commands.Bot(command_prefix='/', intents=intents)

# Define a mapping for model names
model_name_mapping = {
    "abyssorangemix2_Hard": "Abyssorangemix Hard v2.0",
    "babes_30": "Babes v3.0",
    "bambiEyes_v10": "Bambi Eyes v1.0",
    "divineanimemix_V2": "Divine Animemix v2.0",
    "endlessreality_v6": "Endless Reality v6.0",
    "henmixReal_v40": "Henmix Real v4.0",
    "kizukiAnimeHentai_animeHentaiV3": "Kizuki Anime Hentai v3.0",
    "M4RV3LSDUNGEONSNEWV40COMICS_mD40": "M4RV3L-DUNGEON-COMIC v4",
    "majicmixRealistic_v7": "Majic Mix Realistic v7.0",
    "perfectdeliberate_v10": "Perfect Deliverate v1.0",
    "pirsusEpicRealism_pirsusEpicRealismV50": "Pirsus Epic Realism v5.0",
    "restlessexistence_v30Reflection": "Restless Existence v3.0",
    "thisisreal_v50": "This Is Real v5.0",
    "toonyou_beta6": "Toon You v6b",
}

# Define style keywords and their corresponding tags
style_tags = {
    "Anime": ("(anime), (illustration), cartoon, detailed, {prompt}", "deformed, noisy, blurry, realistic, stock photo"),
    "Hentai": ("(ahegao), (anime, hentai painting), naked nao tomori, ({prompt}:1.15), intricate, glossy, realism, art by rossdraws, soft light, (muted colors), warm, dramatic, (cum dripping)", "photo, deformed, black and white, realism, disfigured, low contrast"),
    "Illustration": ("illustration, cartoon, soothing tones, calm colors, {prompt}", "photo, deformed, glitch, noisy, realistic, stock photo"),
    "Caricature": ("big head, big eyes, caricature, a caricature, digital rendering, (figurativism:0.8)", "realistic, deformed, ugly, noisy"),
    "Paper-cut": ("(paper-cut craft:1.2), {prompt}, amazing body, detailed", "noisy, messy, blurry, realistic"),
    "3d Render 👍": ("epic realistic, hyperdetailed, (cycles render:1.3), caustics, (glossy:0.58), (artstation:0.82)", "ugly, deformed, noisy, low poly, blurry, painting"),
    "3d Movie": ("epic realistic, pixar style, disney, (cycles render:1.3), caustics, (glossy:0.58), (artstation:0.2), cute", "sloppy, messy, grainy, highly detailed, ultra textured, photo"),
    "Engraving": ("(grayscale, woodcut:1.2), (etching:1.1), (engraving:0.2), {prompt}, detailed", "colored, blurry, noisy, soft, deformed"),
    "Comic book": ("neutral palette, comic style, muted colors, illustration, cartoon, soothing tones, low saturation, {prompt}", "realistic, photorealistic, blurry, noisy"),
    "Cinematic": ("(cinematic look:1.4), soothing tones, insane details, intricate details, hyperdetailed, low contrast, soft cinematic light, dim colors, exposure blend, hdr, faded, slate gray atmosphere, {prompt}", "grayscale, black and white, monochrome"),
    "Cinematic Horror": ("slate atmosphere, cinematic, dimmed colors, dark shot, muted colors, film grainy, lut, spooky, {prompt}", "anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured"),
    "Gloomy": ("complex background, stuff in the background, highly detailed, (gloomy:1.3), dark, dimmed, hdr, vignette, grimy, (slate atmosphere:0.8), {prompt}", "depth of field, bokeh, blur, blurred, pink"),
    "Professional photo": ("(dark shot:1.4), 80mm, {prompt}, soft light, sharp, exposure blend, medium shot, bokeh, (hdr:1.4), high contrast, (cinematic, teal and orange:0.85), (muted colors, dim colors, soothing tones:1.3), low saturation, (hyperdetailed:1.2), (noir:0.4)", "neon, over saturated"),
    "Painting": ("rutkowski, intricate digital art, soothing tones, (cartoon:0.3), (art:1.4), epic realistic, faded, neutral colors, (hdr:1.4), (muted colors:1.4), (intricate), (artstation:1.99), dramatic, intricate details, (technicolor:0.9), detailed, intricate, cinematic, detailed, {prompt}", "ugly, deformed, noisy, blurry, distorted, grainy"),
    "Painting Vivid": ("(pascal campion:0.38), vivid colors, (painting art:0.06), [eclectic:clear:17], {prompt}", "vignette, cinematic, grayscale, bokeh, blurred, depth of field"),
    "Midjourney Warm": ("epic realistic, {prompt}, faded, (neutral colors:1.2), art, (hdr:1.5), (muted colors:1.1), (pastel:0.2), hyperdetailed, (artstation:1.4), warm lights, dramatic light, (intricate details:1.2), vignette, complex background, rutkowski", "ugly, deformed, noisy, blurry, distorted, grainy"),
    "Midjourney": ("(dark shot:1.1), epic realistic, {prompt}, faded, (neutral colors:1.2), (hdr:1.4), (muted colors:1.2), hyperdetailed, (artstation:1.4), cinematic, warm lights, dramatic light, (intricate details:1.1), complex background, (rutkowski:0.66), (teal and orange:0.4)", "ugly, deformed, noisy, blurry, distorted, grainy"),
    "XpucT": ("epic realistic, {prompt}, (dark shot:1.22), neutral colors, (hdr:1.4), (muted colors:1.4), (intricate), (artstation:1.2), hyperdetailed, dramatic, intricate details, (technicolor:0.9), (rutkowski:0.8), cinematic, detailed", "ugly, deformed, noisy, blurry, distorted, grainy"),
    "+ Details": ("(intricate details:1.12), hdr, (intricate details, hyperdetailed:1.15), {prompt}", "ugly, deformed, noisy, blurry"),
    "Neutral Background": ("(neutral background), {prompt}", "ugly, deformed, noisy, blurry"),
    "Background Black": ("(neutral black background), {prompt}", "ugly, deformed, noisy, blurry"),
    "Background White": ("(neutral white background), {prompt}", "ugly, deformed, noisy, blurry")
}

# Function to parse prompts
def parse_prompt(prompt):
    return prompt

# Function to fetch image from Stable Diffusion
async def fetch_image_from_sd(positive_prompt, negative_prompt, size, model_name, upscaler_model=None, vae_model=None):
    url = "http://127.0.0.1:7860"
    width, height = map(int, size.split('x'))
    payload = {
        "prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        "steps": 40,
        "width": width,
        "height": height,
        "enable_hr": True,
        "hr_scale": 1.5,
        "hr_second_pass_steps": 40,
        "denoising_strength": 0.35,
        "override_settings": {
            "sd_model_checkpoint": model_name,
            "sd_vae": vae_model if vae_model else "None",
        },
        "override_settings_restore_afterwards": False,
    }

    if upscaler_model:
        payload["hr_upscaler"] = upscaler_model

    print(f"[DEBUG] Fetching image with payload: {payload}")

    async with aiohttp.ClientSession() as session:
        async with session.post(url=f'{url}/sdapi/v1/txt2img', json=payload) as response:
            response.raise_for_status()
            r = await response.json()

            if 'images' in r and r['images']:
                image_data = r['images'][0].split(",", 1)[-1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))

                png_payload = {"image": "data:image/png;base64," + image_data}
                async with session.post(url=f'{url}/sdapi/v1/png-info', json=png_payload) as response2:
                    response2.raise_for_status()
                    info_text = await response2.json()

                pnginfo = PngImagePlugin.PngInfo()
                if info_text:
                    pnginfo.add_text("parameters", info_text.get("info", ""))

                print("[DEBUG] Image fetched successfully")
                return image, pnginfo
            else:
                print("[DEBUG] No images found in response")
                return None, None

@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.emoji) == "🚫":
        # Fetch the channel
        if payload.guild_id is None:  # If this is a DM
            channel = await bot.fetch_channel(payload.channel_id)
        else:  # If this is within a guild
            channel = bot.get_channel(payload.channel_id)

        if channel:
            message = await channel.fetch_message(payload.message_id)
            if message.author == bot.user:
                # In DMs, anyone can delete the bot's messages
                if payload.guild_id is None:
                    await message.delete()
                else:
                    # In guilds, check if the user who reacted is an admin
                    guild = bot.get_guild(payload.guild_id)
                    member = guild.get_member(payload.user_id)
                    if member and member.guild_permissions.administrator:
                        await message.delete()

# Function to save image
def save_image(image, path):
    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    image_filename = f"{timestamp}.png"
    image_path = os.path.join(path, image_filename)
    image.save(image_path, 'PNG')
    print(f"[DEBUG] Image saved at: {image_path}")
    return image_path

# Database functions
def initialize_db():
    conn = sqlite3.connect('prompts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS used_prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    prompt_file TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

def add_used_prompt(prompt, prompt_file):
    conn = sqlite3.connect('prompts.db')
    c = conn.cursor()
    c.execute('INSERT INTO used_prompts (prompt, prompt_file) VALUES (?, ?)', (prompt, prompt_file))
    conn.commit()
    conn.close()

def get_used_prompts(prompt_file):
    conn = sqlite3.connect('prompts.db')
    c = conn.cursor()
    c.execute('SELECT prompt FROM used_prompts WHERE prompt_file = ?', (prompt_file,))
    used_prompts = c.fetchall()
    conn.close()
    return [prompt[0] for prompt in used_prompts]

def clear_used_prompts(prompt_file):
    conn = sqlite3.connect('prompts.db')
    c = conn.cursor()
    c.execute('DELETE FROM used_prompts WHERE prompt_file = ?', (prompt_file,))
    conn.commit()
    conn.close()

# Scheduler to generate art based on prompts
@tasks.loop(minutes=2)  # Default interval, adjusted later
async def scheduled_prompt():
    print("[DEBUG] Running scheduled_prompt...")
    channel = bot.get_channel(1170896742766624819)  # Replace with your channel ID
    if channel:
        global current_prompt_file_index
        prompt_file = prompt_files_to_use[current_prompt_file_index]
        print(f"[DEBUG] Using prompt file: {prompt_file}")

        try:
            with open(f'./ASSETS/{prompt_file}', 'r') as f:
                prompts = f.readlines()
            print(f"[DEBUG] Loaded prompts: {prompts}")

            used_prompts = get_used_prompts(prompt_file)
            available_prompts = [line for line in prompts if line not in used_prompts]

            if not available_prompts:
                clear_used_prompts(prompt_file)
                available_prompts = prompts

            selected_prompt = random.choice(available_prompts)
            add_used_prompt(selected_prompt, prompt_file)

            print(f"[DEBUG] Processing line: {selected_prompt}")
            parts = selected_prompt.strip().split('" "')
            if len(parts) == 3:
                rating, prompt_text, model_name = parts[0].strip('"'), parts[1], parts[2].strip('"')
                if model_name == "random":
                    model_name = random.choice(list(model_name_mapping.keys()))
                parsed_prompt = parse_prompt(prompt_text)

                # Add two random styles
                style1_key, style2_key = random.sample(list(style_tags.keys()), 2)
                style1, style2 = style_tags[style1_key], style_tags[style2_key]
                positive_prompt = f"{parsed_prompt}, {style1[0].format(prompt=parsed_prompt)}, {style2[0].format(prompt=parsed_prompt)}"
                negative_prompt = f"{style1[1]}, {style2[1]}"

                print(f"[DEBUG] Using prompt: {positive_prompt} with negative prompt: {negative_prompt}, model: {model_name_mapping[model_name]}, rating: {rating}")

                # Fetch image
                image, pnginfo = await fetch_image_from_sd(positive_prompt, negative_prompt, "720x405", model_name,
                                                           upscaler_model="4x-UltraSharp",
                                                           vae_model="vaeFtMse840000EmaPruned_vae.safetensors")
                if image:
                    # Save image
                    image_path = save_image(image, './SD_IMAGES')

                    # Create the embed
                    embed = discord.Embed(title=f'A.I. Generated {rating.upper()} Art',
                                          description=f'**Model:** {model_name_mapping[model_name]}\n'
                                                      f'**Prompt:** {prompt_text}\n'
                                                      f'**Styles:** {style1_key}, {style2_key}\n\n',
                                          color=0x5dade2)
                    embed.set_image(url='attachment://image.png')

                    await channel.send(file=discord.File(image_path, filename='image.png'), embed=embed)
                    print(f"[DEBUG] Sent prompt: {positive_prompt} with negative prompt: {negative_prompt}, model: {model_name_mapping[model_name]} and rating: {rating}")
                else:
                    print("[DEBUG] No image generated")
                await asyncio.sleep(10)  # Adjust as needed
            else:
                print("[DEBUG] Line format incorrect, skipping line.")
        except Exception as e:
            print(f"[DEBUG] Error reading or processing {prompt_file}: {e}")

        # Move to the next prompt file for the next cycle
        current_prompt_file_index = (current_prompt_file_index + 1) % len(prompt_files_to_use)
    else:
        print("[DEBUG] Channel not found.")

@bot.tree.command(name='purge', description='Clear the bot\'s messages from the channel.')
async def purge(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)  # Acknowledge the command immediately with a deferred ephemeral response

    try:
        print("Purge command invoked. Resetting the sent status of all entries.")

        # Remove bot's messages from the channel
        channel = interaction.channel
        if channel:
            async for message in channel.history(limit=2500):
                if message.author == bot.user:
                    await message.delete()
                    await asyncio.sleep(1)  # Add delay to prevent rate limiting
            print(f"Bot messages in channel '{channel.name}' have been cleared.")
        else:
            print("Channel not found. Cannot clear messages.")

    except Exception as e:
        print(f"Error during purge operation: {e}")

    # Inform the user that the purge is complete
    await interaction.followup.send("Purge completed. All articles are marked as unsent.", ephemeral=True)
    print("Purge operation completed.")

# Artshow command to manage the scheduled prompts
@app_commands.command(name='artshow', description='Manage the scheduled prompts')
@app_commands.describe(interval='Interval in minutes for the scheduled prompts', file_number='Specific prompt file number to use (optional)')
async def artshow(interaction: discord.Interaction, interval: int, file_number: str = None):
    global current_prompt_file_index
    global prompt_files_to_use
    all_files = list(range(1, len(prompt_files) + 1))

    if interval == 0:
        if not scheduled_prompt.is_running():
            await interaction.response.send_message("Scheduler is not running.", ephemeral=True)
            print("[DEBUG] Scheduler is not running.")
        else:
            scheduled_prompt.stop()
            await interaction.response.send_message("Scheduler stopped.", ephemeral=True)
            print("[DEBUG] Scheduler stopped.")
    else:
        if file_number:
            try:
                files_to_use = parse_file_selection(file_number, all_files)
                prompt_files_to_use = [prompt_files[i - 1] for i in files_to_use]
                current_prompt_file_index = 0
                await interaction.response.send_message(f"Scheduler started with an interval of {interval} minutes using {', '.join(prompt_files_to_use)}.", ephemeral=True)
                print(f"[DEBUG] Scheduler started with an interval of {interval} minutes using {', '.join(prompt_files_to_use)}.")
            except ValueError as e:
                await interaction.response.send_message(str(e), ephemeral=True)
                print(f"[DEBUG] {str(e)}")
                return
        else:
            prompt_files_to_use = prompt_files  # Use all files if no specific file number is given
            current_prompt_file_index = 0
            await interaction.response.send_message(f"Scheduler started with an interval of {interval} minutes using all prompt files.", ephemeral=True)
            print(f"[DEBUG] Scheduler started with an interval of {interval} minutes using all prompt files.")

        scheduled_prompt.change_interval(minutes=interval)
        if not scheduled_prompt.is_running():
            scheduled_prompt.start()

def parse_file_selection(selection, all_files):
    selected_files = set()
    ranges = selection.split(',')
    for r in ranges:
        if '-' in r:
            start, end = map(int, r.split('-'))
            selected_files.update(range(start, end + 1))
        else:
            selected_files.add(int(r))
    if not selected_files.issubset(all_files):
        raise ValueError(f"Invalid file selection. Please select from 1 to {max(all_files)}.")
    return sorted(selected_files)

@bot.event
async def on_ready():
    global current_prompt_file_index
    global prompt_files
    global prompt_files_to_use

    current_prompt_file_index = 0  # Initialize the index for cycling through prompt files

    # Dynamically load prompt files and sort them numerically
    prompt_files = sorted(
        [os.path.basename(f) for f in glob.glob('./ASSETS/prompts_*.txt')],
        key=lambda x: int(re.search(r'\d+', x).group())
    )

    prompt_files_to_use = prompt_files  # Default to using all files

    print(f'Bot is ready. Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        bot.tree.add_command(artshow)
        await bot.tree.sync()
        print(f"Synced {len(bot.tree.get_commands())} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Get the bot token from the environment variable
bot_token = os.getenv('ARTSHOW_DISCORD_BOT_TOKEN')

if bot_token is None:
    print("Bot token not found. Please set the ARTSHOW_DISCORD_BOT_TOKEN environment variable.")
else:
    bot.run(bot_token)

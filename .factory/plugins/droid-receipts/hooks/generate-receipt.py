#!/usr/bin/env python3
"""
Droid Receipts - Generate visual receipts for Droid sessions.

Triggered by SessionEnd hook. Reads session data from:
- Hook stdin (session_id, transcript_path, cwd)
- Session settings JSON (token counts, model)
- Transcript JSONL (session title, timestamps)

Generates an SVG receipt saved to ~/.factory/receipts/
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Pricing: $1 per 1 million tokens
PRICE_PER_MILLION = 1.0

# Output directory for receipts
RECEIPTS_DIR = Path.home() / ".factory" / "receipts"


def format_currency(tokens: int) -> str:
    """Calculate cost at $1/M tokens."""
    cost = tokens / 1_000_000 * PRICE_PER_MILLION
    return f"${cost:.2f}"


def format_number(n: int) -> str:
    """Format number with thousand separators."""
    return f"{n:,}"


def format_duration(ms: int) -> str:
    """Format duration from milliseconds."""
    seconds = ms // 1000
    minutes = seconds // 60
    hours = minutes // 60
    
    if hours > 0:
        return f"{hours}h {minutes % 60}m {seconds % 60}s"
    elif minutes > 0:
        return f"{minutes}m {seconds % 60}s"
    else:
        return f"{seconds}s"


def get_model_name(model: str) -> str:
    """Clean up model name for display."""
    model_map = {
        "claude-opus-4-6": "Claude Opus 4.6",
        "claude-opus-4-6-fast": "Claude Opus 4.6 Fast",
        "claude-opus-4-5-20251101": "Claude Opus 4.5",
        "claude-sonnet-4-5-20250929": "Claude Sonnet 4.5",
        "claude-haiku-4-5-20251001": "Claude Haiku 4.5",
        "gpt-5.1-codex-max": "GPT-5.1 Codex Max",
        "gpt-5.1-codex": "GPT-5.1 Codex",
        "gpt-5.1": "GPT-5.1",
        "gpt-5.2": "GPT-5.2",
        "gpt-5.2-codex": "GPT-5.2 Codex",
        "gpt-5.3-codex": "GPT-5.3 Codex",
        "gemini-3-pro-preview": "Gemini 3 Pro",
        "gemini-3-flash-preview": "Gemini 3 Flash",
        "glm-4.7": "Droid Core (GLM-4.7)",
        "glm-5": "Droid Core (GLM-5)",
        "kimi-k2.5": "Droid Core (Kimi K2.5)",
        "minimax-m2.5": "MiniMax M2.5",
    }
    return model_map.get(model, model)


def escape_xml(text: str) -> str:
    """Escape XML special characters."""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;"))


def generate_svg(session_data: dict) -> str:
    """Generate SVG receipt from session data."""
    
    # Extract data
    session_id = session_data["session_id"]
    session_title = session_data.get("title", "Droid Session")[:40]
    location = session_data.get("location", "The Cloud")[:30]
    model = session_data["model"]
    model_name = get_model_name(model)
    tokens = session_data["tokens"]
    end_time = session_data.get("end_time", datetime.now().isoformat())
    active_time = session_data.get("active_time_ms", 0)
    
    # Calculate totals
    input_tokens = tokens.get("inputTokens", 0)
    output_tokens = tokens.get("outputTokens", 0)
    cache_write = tokens.get("cacheCreationTokens", 0)
    cache_read = tokens.get("cacheReadTokens", 0)
    total_tokens = input_tokens + output_tokens
    
    input_cost = format_currency(input_tokens)
    output_cost = format_currency(output_tokens)
    cache_write_cost = format_currency(cache_write)
    cache_read_cost = format_currency(cache_read)
    total_cost = format_currency(total_tokens)
    
    # Format date
    try:
        dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        date_str = end_time
    
    # Format duration
    duration_str = format_duration(active_time)
    
    # Escape text for XML
    session_title = escape_xml(session_title)
    location = escape_xml(location)
    model_name = escape_xml(model_name)
    
    # Factory logo (simplified SVG path)
    logo_path = '''M500.76 329.29C499.9 329.077 499.097 328.68 498.404 328.128C497.712 327.575 497.146 326.88 496.748 326.089C496.349 325.298 496.126 324.43 496.093 323.545C496.061 322.659 496.22 321.778 496.56 320.96C508.3 292.39 513.48 269.53 505.12 259.96C482.98 234.57 394.19 285.059 365.88 302.159C365.122 302.615 364.274 302.902 363.395 303C362.516 303.098 361.626 303.005 360.786 302.728C359.946 302.451 359.175 301.996 358.527 301.394C357.879 300.792 357.369 300.057 357.03 299.24C345.13 270.73 332.62 250.9 319.94 250.04C286.33 247.74 259.24 346.229 251.31 378.329C251.098 379.189 250.703 379.993 250.152 380.685C249.6 381.378 248.905 381.943 248.115 382.342C247.325 382.741 246.458 382.964 245.573 382.996C244.689 383.029 243.808 382.87 242.99 382.53C214.42 370.79 191.55 365.61 181.99 373.97C156.6 396.11 207.08 484.9 224.18 513.21C224.637 513.967 224.925 514.815 225.024 515.695C225.123 516.574 225.031 517.465 224.754 518.305C224.477 519.146 224.021 519.917 223.418 520.565C222.815 521.213 222.079 521.722 221.26 522.059C192.76 533.959 172.93 546.469 172.06 559.149C169.77 592.759 268.25 619.85 300.36 627.78C301.218 627.994 302.019 628.391 302.71 628.943C303.4 629.495 303.964 630.19 304.361 630.98C304.759 631.769 304.982 632.635 305.014 633.519C305.047 634.402 304.889 635.283 304.55 636.099C292.81 664.669 287.63 687.539 295.99 697.099C318.13 722.489 406.93 672.009 435.24 654.909'''
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="680" viewBox="0 0 400 680" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .receipt-bg {{ fill: #f8f8f8; }}
      .text {{ font-family: 'Courier New', Courier, monospace; font-size: 12px; fill: #333; }}
      .text-bold {{ font-family: 'Courier New', Courier, monospace; font-size: 12px; fill: #333; font-weight: bold; }}
      .text-large {{ font-family: 'Courier New', Courier, monospace; font-size: 14px; fill: #333; }}
      .text-small {{ font-family: 'Courier New', Courier, monospace; font-size: 10px; fill: #666; }}
      .separator {{ stroke: #333; stroke-width: 2; }}
      .light-separator {{ stroke: #999; stroke-width: 1; stroke-dasharray: 2,2; }}
      .logo {{ fill: #333; }}
    </style>
  </defs>
  
  <!-- Receipt background -->
  <rect class="receipt-bg" x="10" y="10" width="380" height="660" rx="3"/>
  
  <!-- Top zigzag edge -->
  <path d="M10 25 L30 10 L50 25 L70 10 L90 25 L110 10 L130 25 L150 10 L170 25 L190 10 L210 25 L230 10 L250 25 L270 10 L290 25 L310 10 L330 25 L350 10 L370 25 L390 10" fill="#3a3a3a"/>
  
  <!-- Factory Logo -->
  <g transform="translate(130, 50) scale(0.12)">
    <path class="logo" d="{logo_path}"/>
  </g>
  
  <!-- DROID text -->
  <text x="200" y="145" class="text-large text-bold" text-anchor="middle" font-size="18">FACTORY</text>
  <text x="200" y="165" class="text-small" text-anchor="middle">DROID RECEIPT</text>
  
  <!-- Separator -->
  <line x1="30" y1="185" x2="370" y2="185" class="separator"/>
  
  <!-- Session info -->
  <text x="30" y="210" class="text">Location</text>
  <text x="370" y="210" class="text" text-anchor="end">{location}</text>
  <line x1="100" y1="206" x2="290" y2="206" class="light-separator"/>
  
  <text x="30" y="230" class="text">Session</text>
  <text x="370" y="230" class="text" text-anchor="end">{session_title}</text>
  <line x1="100" y1="226" x2="290" y2="226" class="light-separator"/>
  
  <text x="30" y="250" class="text">Date</text>
  <text x="370" y="250" class="text" text-anchor="end">{date_str}</text>
  <line x1="100" y1="246" x2="290" y2="246" class="light-separator"/>
  
  <text x="30" y="270" class="text">Duration</text>
  <text x="370" y="270" class="text" text-anchor="end">{duration_str}</text>
  <line x1="100" y1="266" x2="290" y2="266" class="light-separator"/>
  
  <!-- Separator -->
  <line x1="30" y1="290" x2="370" y2="290" class="separator"/>
  
  <!-- Header -->
  <text x="30" y="315" class="text-bold">ITEM</text>
  <text x="200" y="315" class="text-bold" text-anchor="middle">QTY</text>
  <text x="370" y="315" class="text-bold" text-anchor="end">PRICE</text>
  
  <line x1="30" y1="325" x2="370" y2="325" class="light-separator"/>
  
  <!-- Model name -->
  <text x="30" y="350" class="text-bold">{model_name}</text>
  
  <!-- Line items -->
  <text x="45" y="375" class="text">Input tokens</text>
  <text x="200" y="375" class="text" text-anchor="middle">{format_number(input_tokens)}</text>
  <text x="370" y="375" class="text" text-anchor="end">{input_cost}</text>
  
  <text x="45" y="395" class="text">Output tokens</text>
  <text x="200" y="395" class="text" text-anchor="middle">{format_number(output_tokens)}</text>
  <text x="370" y="395" class="text" text-anchor="end">{output_cost}</text>'''
    
    # Add cache tokens if present
    if cache_write > 0:
        svg += f'''
  <text x="45" y="415" class="text">Cache write</text>
  <text x="200" y="415" class="text" text-anchor="middle">{format_number(cache_write)}</text>
  <text x="370" y="415" class="text" text-anchor="end">{cache_write_cost}</text>'''
    
    if cache_read > 0:
        y_pos = 435 if cache_write > 0 else 415
        svg += f'''
  <text x="45" y="{y_pos}" class="text">Cache read</text>
  <text x="200" y="{y_pos}" class="text" text-anchor="middle">{format_number(cache_read)}</text>
  <text x="370" y="{y_pos}" class="text" text-anchor="end">{cache_read_cost}</text>'''
    
    # Calculate total section position
    total_y = 435
    if cache_write > 0:
        total_y += 20
    if cache_read > 0:
        total_y += 20
    
    svg += f'''
  
  <!-- Total section -->
  <line x1="30" y1="{total_y + 10}" x2="370" y2="{total_y + 10}" class="separator"/>
  
  <text x="30" y="{total_y + 35}" class="text-bold">TOTAL</text>
  <text x="370" y="{total_y + 35}" class="text-bold" text-anchor="end">{total_cost}</text>
  
  <line x1="30" y1="{total_y + 45}" x2="370" y2="{total_y + 45}" class="separator"/>
  
  <!-- Footer -->
  <text x="200" y="{total_y + 75}" class="text" text-anchor="middle">CASHIER: {model_name}</text>
  
  <text x="200" y="{total_y + 105}" class="text" text-anchor="middle">Thank you for building!</text>
  
  <line x1="100" y1="{total_y + 125}" x2="300" y2="{total_y + 125}" class="light-separator"/>
  
  <text x="200" y="{total_y + 145}" class="text-small" text-anchor="middle">github.com/Factory-AI/factory</text>
  
  <!-- Bottom zigzag edge -->
  <path d="M10 665 L30 680 L50 665 L70 680 L90 665 L110 680 L130 665 L150 680 L170 665 L190 680 L210 665 L230 680 L250 665 L270 680 L290 665 L310 680 L330 665 L350 680 L370 665 L390 680" fill="#3a3a3a"/>
</svg>'''
    
    return svg


def main():
    try:
        # Read hook input from stdin
        hook_input = json.load(sys.stdin)
        
        session_id = hook_input.get("session_id", "")
        transcript_path = hook_input.get("transcript_path", "").replace("~", os.environ.get("HOME", "~"))
        cwd = hook_input.get("cwd", "")
        
        # Extract location from cwd
        location = Path(cwd).name if cwd else "The Cloud"
        
        # Read session settings
        settings_path = transcript_path.replace(".jsonl", ".settings.json")
        
        if not os.path.exists(settings_path):
            print(f"No session settings found at {settings_path}", file=sys.stderr)
            sys.exit(0)  # Non-blocking exit
        
        with open(settings_path, "r") as f:
            settings = json.load(f)
        
        tokens = settings.get("tokenUsage", {})
        model = settings.get("model", "unknown")
        active_time_ms = settings.get("assistantActiveTimeMs", 0)
        
        # Skip if no token data
        if not tokens:
            print("No token usage data available", file=sys.stderr)
            sys.exit(0)
        
        # Parse transcript for session title and end time
        session_title = "Droid Session"
        end_time = datetime.now().isoformat()
        
        if os.path.exists(transcript_path):
            with open(transcript_path, "r") as f:
                first_line = f.readline().strip()
                if first_line:
                    try:
                        first_entry = json.loads(first_line)
                        session_title = first_entry.get("title", session_title)
                    except:
                        pass
                
                # Get last timestamp
                for line in reversed(list(f)):
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            if "timestamp" in entry:
                                end_time = entry["timestamp"]
                                break
                        except:
                            pass
        
        # Build session data
        session_data = {
            "session_id": session_id,
            "title": session_title,
            "location": location,
            "model": model,
            "tokens": tokens,
            "end_time": end_time,
            "active_time_ms": active_time_ms,
        }
        
        # Create output directory
        RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate SVG
        svg_content = generate_svg(session_data)
        
        # Save receipt
        output_path = RECEIPTS_DIR / f"{session_id}.svg"
        with open(output_path, "w") as f:
            f.write(svg_content)
        
        print(f"Receipt saved to {output_path}")
        
        # Optionally open in browser (macOS)
        if sys.platform == "darwin":
            os.system(f'open "{output_path}"')
        
    except Exception as e:
        print(f"Error generating receipt: {e}", file=sys.stderr)
        sys.exit(0)  # Non-blocking exit


if __name__ == "__main__":
    main()

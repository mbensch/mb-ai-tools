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
# Cache tokens are billed at 1/10 of standard tokens
CACHE_PRICE_MULTIPLIER = 0.1

# Output directory for receipts
RECEIPTS_DIR = Path.home() / ".factory" / "receipts"


def format_currency(tokens: int) -> str:
    """Calculate cost at $1/M tokens."""
    cost = tokens / 1_000_000 * PRICE_PER_MILLION
    return f"${cost:.2f}"


def format_cache_currency(tokens: int) -> str:
    """Calculate cache token cost at 1/10 price."""
    cost = tokens / 1_000_000 * PRICE_PER_MILLION * CACHE_PRICE_MULTIPLIER
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


def generate_droid_name(session_id: str) -> str:
    """Generate a Star Wars-style droid name from session ID."""
    # Extract hex-like characters from session ID
    hex_chars = "".join(c for c in session_id.upper() if c in "0123456789ABCDEF")
    
    # Pad if needed
    if len(hex_chars) < 8:
        hex_chars = hex_chars.ljust(8, "0")
    
    # Star Wars droid prefixes
    prefixes = ["R2", "C3", "BB", "K2", "IG", "BD", "QT", "AP", "RX", "TC", "GNK", "WED"]
    
    # Use first hex digit to pick prefix
    prefix_idx = int(hex_chars[0], 16) % len(prefixes)
    prefix = prefixes[prefix_idx]
    
    # Generate model number from remaining hex
    model_num = hex_chars[1:4]
    
    return f"{prefix}-{model_num}"


def escape_xml(text: str) -> str:
    """Escape XML special characters."""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;"))


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;"))


def generate_html(session_data: dict) -> str:
    """Generate HTML receipt from session data."""
    
    # Extract data
    session_id = session_data["session_id"]
    session_short = session_id[:8] if len(session_id) >= 8 else session_id
    location = session_data.get("location", "The Cloud")[:30]
    model = session_data["model"]
    model_name = get_model_name(model)
    droid_name = generate_droid_name(session_id)
    tokens = session_data["tokens"]
    end_time = session_data.get("end_time", datetime.now().isoformat())
    active_time = session_data.get("active_time_ms", 0)
    
    # Calculate totals
    input_tokens = tokens.get("inputTokens", 0)
    output_tokens = tokens.get("outputTokens", 0)
    cache_write = tokens.get("cacheCreationTokens", 0)
    cache_read = tokens.get("cacheReadTokens", 0)
    
    # Total tokens for display (sum of all)
    total_tokens = input_tokens + output_tokens + cache_write + cache_read
    
    # Total cost: regular tokens at $1/M, cache tokens at $0.10/M
    total_cost = (
        (input_tokens + output_tokens) / 1_000_000 * PRICE_PER_MILLION +
        (cache_write + cache_read) / 1_000_000 * PRICE_PER_MILLION * CACHE_PRICE_MULTIPLIER
    )
    total_cost_str = f"${total_cost:.2f}"
    
    # Format date
    try:
        dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        date_str = end_time
    
    duration_str = format_duration(active_time)
    
    # Escape text
    location = escape_html(location)
    model_name = escape_html(model_name)
    droid_name = escape_html(droid_name)
    session_short = escape_html(session_short)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Droid Receipt - {session_short}</title>
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    
    body {{
      font-family: 'Courier New', Courier, monospace;
      font-size: 14px;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}
    
    .receipt {{
      background: #fafafa;
      width: 400px;
      padding: 30px 25px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
      border-radius: 4px;
      animation: slideIn 0.5s ease-out;
    }}
    
    @keyframes slideIn {{
      from {{ opacity: 0; transform: translateY(-20px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .header {{
      text-align: center;
      padding-bottom: 20px;
      border-bottom: 2px solid #333;
    }}
    
    .logo {{
      margin-bottom: 10px;
    }}
    
    .logo svg {{
      height: 50px;
      width: auto;
    }}
    
    .subtitle {{
      font-size: 11px;
      color: #666;
      letter-spacing: 2px;
    }}
    
    .model-badge {{
      background: #333;
      color: #fff;
      padding: 8px 16px;
      border-radius: 20px;
      display: inline-block;
      margin: 20px 0;
      font-size: 12px;
      font-weight: bold;
    }}
    
    .meta {{
      margin: 15px 0;
    }}
    
    .meta-row {{
      display: flex;
      justify-content: space-between;
      padding: 5px 0;
      border-bottom: 1px dashed #ccc;
    }}
    
    .meta-row:last-child {{
      border-bottom: none;
    }}
    
    .meta-label {{
      color: #666;
    }}
    
    .meta-value {{
      color: #333;
      font-weight: 500;
    }}
    
    .separator {{
      border-bottom: 2px solid #333;
      margin: 15px 0;
    }}
    
    .items-header {{
      display: flex;
      justify-content: space-between;
      padding: 10px 0;
      font-weight: bold;
      border-bottom: 1px dashed #ccc;
    }}
    
    .item {{
      margin: 8px 0;
    }}
    
    .item-row {{
      display: flex;
      justify-content: space-between;
      padding: 3px 0;
      color: #555;
    }}
    
    .item-row .qty {{
      text-align: center;
      flex: 1;
    }}
    
    .item-row .price {{
      text-align: right;
      min-width: 80px;
    }}
    
    .item-label {{
      min-width: 120px;
    }}
    
    .total-section {{
      border-top: 2px solid #333;
      margin-top: 15px;
      padding-top: 15px;
    }}
    
    .total-row {{
      display: flex;
      justify-content: space-between;
      font-size: 18px;
      font-weight: bold;
      padding: 5px 0;
    }}
    
    .footer {{
      text-align: center;
      margin-top: 25px;
      padding-top: 20px;
      border-top: 2px dashed #ccc;
    }}
    
    .cashier {{
      color: #333;
      margin-bottom: 15px;
    }}
    
    .thank-you {{
      font-size: 13px;
      color: #333;
      margin-bottom: 15px;
    }}
    
    .github-link {{
      font-size: 11px;
      color: #999;
    }}
    
    .github-link a {{
      color: #666;
      text-decoration: none;
    }}
    
    .github-link a:hover {{
      color: #333;
    }}
    
    @media print {{
      body {{
        background: white;
      }}
      .receipt {{
        box-shadow: none;
      }}
    }}
  </style>
</head>
<body>
  <div class="receipt">
    <div class="header">
      <div class="logo">
        <svg viewBox="0 0 3402 957" xmlns="http://www.w3.org/2000/svg">
          <!-- Factory Icon (spinning wheel) -->
          <path fill="#333" d="M500.76 329.29C499.9 329.077 499.097 328.68 498.404 328.128C497.712 327.575 497.146 326.88 496.748 326.089C496.349 325.298 496.126 324.43 496.093 323.545C496.061 322.659 496.22 321.778 496.56 320.96C508.3 292.39 513.48 269.53 505.12 259.96C482.98 234.57 394.19 285.059 365.88 302.159C365.122 302.615 364.274 302.902 363.395 303C362.516 303.098 361.626 303.005 360.786 302.728C359.946 302.451 359.175 301.996 358.527 301.394C357.879 300.792 357.369 300.057 357.03 299.24C345.13 270.73 332.62 250.9 319.94 250.04C286.33 247.74 259.24 346.229 251.31 378.329C251.098 379.189 250.703 379.993 250.152 380.685C249.6 381.378 248.905 381.943 248.115 382.342C247.325 382.741 246.458 382.964 245.573 382.996C244.689 383.029 243.808 382.87 242.99 382.53C214.42 370.79 191.55 365.61 181.99 373.97C156.6 396.11 207.08 484.9 224.18 513.21C224.637 513.967 224.925 514.815 225.024 515.695C225.123 516.574 225.031 517.465 224.754 518.305C224.477 519.146 224.021 519.917 223.418 520.565C222.815 521.213 222.079 521.722 221.26 522.059C192.76 533.959 172.93 546.469 172.06 559.149C169.77 592.759 268.25 619.85 300.36 627.78C301.218 627.994 302.019 628.391 302.71 628.943C303.4 629.495 303.964 630.19 304.361 630.98C304.759 631.769 304.982 632.635 305.014 633.519C305.047 634.402 304.889 635.283 304.55 636.099C292.81 664.669 287.63 687.539 295.99 697.099C318.13 722.489 406.93 672.009 435.24 654.909C435.998 654.452 436.846 654.164 437.726 654.065C438.605 653.966 439.496 654.058 440.336 654.336C441.177 654.613 441.947 655.069 442.595 655.672C443.243 656.275 443.753 657.011 444.09 657.829C455.99 686.329 468.49 706.16 481.18 707.03C514.79 709.32 541.88 610.84 549.8 578.73C550.014 577.871 550.411 577.068 550.964 576.377C551.517 575.685 552.213 575.121 553.004 574.723C553.795 574.326 554.662 574.103 555.547 574.072C556.432 574.04 557.313 574.199 558.13 574.54C586.7 586.28 609.56 591.449 619.13 583.099C644.52 560.959 594.03 472.159 576.93 443.849C576.476 443.091 576.191 442.243 576.094 441.365C575.996 440.486 576.09 439.596 576.367 438.757C576.644 437.917 577.098 437.147 577.699 436.499C578.3 435.851 579.034 435.339 579.85 435C608.36 423.1 628.19 410.589 629.05 397.909C631.35 364.299 532.86 337.21 500.76 329.29ZM462.2 297.069C468.66 308.649 435.37 385.81 410.61 439.78C410.196 440.682 409.516 441.436 408.66 441.94C407.805 442.444 406.815 442.674 405.825 442.599C404.835 442.524 403.891 442.147 403.122 441.52C402.352 440.892 401.793 440.044 401.52 439.089C391.52 403.999 380.09 362.77 367.86 327.77C367.38 326.396 367.404 324.896 367.928 323.539C368.452 322.181 369.442 321.054 370.72 320.359C401.26 303.679 453.52 281.529 462.2 297.069ZM315.84 306.619C328.59 310.239 359.61 388.34 380.26 444.01C380.605 444.94 380.656 445.953 380.408 446.914C380.159 447.874 379.623 448.735 378.871 449.382C378.118 450.029 377.186 450.43 376.199 450.531C375.212 450.633 374.218 450.43 373.35 449.95C341.44 432.24 304.23 411.14 270.83 395.04C269.522 394.405 268.482 393.328 267.894 391.998C267.306 390.669 267.209 389.174 267.62 387.78C277.45 354.42 298.71 301.769 315.84 306.619ZM219.1 416.869C230.67 410.409 307.84 443.7 361.8 468.46C362.703 468.874 363.457 469.554 363.961 470.41C364.465 471.265 364.695 472.255 364.62 473.245C364.544 474.235 364.168 475.178 363.54 475.948C362.913 476.717 362.065 477.277 361.11 477.55C326.03 487.55 284.79 498.98 249.79 511.21C248.418 511.687 246.92 511.662 245.565 511.138C244.21 510.614 243.084 509.626 242.39 508.349C225.74 477.809 203.55 425.549 219.1 416.869ZM228.65 563.23C232.26 550.48 310.37 519.459 366.04 498.809C366.97 498.465 367.984 498.414 368.944 498.662C369.905 498.911 370.766 499.447 371.413 500.199C372.059 500.951 372.461 501.884 372.562 502.87C372.663 503.857 372.46 504.851 371.98 505.72C354.26 537.63 333.16 574.84 317.06 608.23C316.431 609.542 315.354 610.587 314.023 611.177C312.693 611.767 311.196 611.864 309.8 611.45C276.44 601.68 223.79 580.36 228.65 563.23ZM338.9 659.97C332.43 648.4 365.73 571.23 390.49 517.27C390.904 516.367 391.585 515.613 392.44 515.109C393.296 514.605 394.285 514.375 395.275 514.45C396.266 514.525 397.209 514.902 397.978 515.529C398.748 516.157 399.307 517.005 399.58 517.96C409.58 553.04 421.01 594.28 433.24 629.28C433.717 630.653 433.69 632.151 433.165 633.507C432.639 634.862 431.648 635.987 430.37 636.68C399.84 653.33 347.57 675.52 338.93 659.97H338.9ZM485.26 650.419C472.5 646.809 441.48 568.7 420.83 513.03C420.484 512.098 420.431 511.082 420.68 510.12C420.928 509.158 421.466 508.295 422.22 507.648C422.974 507 423.909 506.6 424.897 506.5C425.886 506.4 426.882 506.606 427.75 507.089C459.65 524.799 496.87 545.91 530.26 562.01C531.571 562.641 532.613 563.718 533.202 565.048C533.79 566.379 533.885 567.875 533.47 569.27C523.65 602.68 502.39 655.279 485.26 650.419ZM582 540.169C570.42 546.639 493.26 513.339 439.29 488.579C438.387 488.165 437.633 487.485 437.129 486.629C436.625 485.774 436.396 484.784 436.471 483.794C436.546 482.804 436.922 481.861 437.55 481.091C438.177 480.321 439.025 479.763 439.98 479.49C475.07 469.49 516.3 458.059 551.3 445.829C552.675 445.352 554.175 445.378 555.532 445.904C556.889 446.43 558.015 447.421 558.71 448.7C575.35 479.23 597.54 531.499 582 540.169ZM572.45 393.809C568.83 406.569 490.73 437.59 435.06 458.24C434.128 458.586 433.113 458.638 432.151 458.39C431.189 458.141 430.326 457.604 429.678 456.85C429.031 456.096 428.631 455.161 428.531 454.172C428.431 453.184 428.636 452.188 429.12 451.319C446.83 419.419 467.93 382.199 484.03 348.809C484.663 347.5 485.74 346.459 487.07 345.871C488.4 345.283 489.896 345.186 491.29 345.599C524.65 355.419 577.3 376.679 572.45 393.809Z"/>
          <!-- FACTORY text -->
          <path fill="#333" d="M850.34 642.2V314.85H1089.34V373.3H913.5V450H1070.63V506.58H913.5V642.2H850.34Z"/>
          <path fill="#333" d="M1130.47 642.2L1228.55 360.8C1233.23 347.375 1241.97 335.739 1253.57 327.506C1265.16 319.273 1279.02 314.849 1293.24 314.85C1307.55 314.848 1321.5 319.327 1333.13 327.658C1344.76 335.989 1353.49 347.753 1358.1 361.3L1453.61 642.2H1388.61L1365.69 573.92H1219.79L1195.94 642.2H1130.47ZM1238.47 516.87H1346.97L1307.75 398.87C1303.07 384.77 1283.15 384.72 1278.4 398.79L1238.47 516.87Z"/>
          <path fill="#333" d="M1502.72 478.52C1502.72 386.4 1577.07 311.1 1669.2 311.1C1737.01 311.1 1792.2 352.26 1818.38 410.71L1758.52 428.02C1741.69 394.81 1710.82 370.96 1669.2 370.96C1609.34 370.96 1565.38 418.66 1565.38 478.52C1565.38 538.38 1609.38 585.61 1669.2 585.61C1710.82 585.61 1740.75 564.1 1757.12 530.43L1817.91 546.8C1792.19 604.8 1737.48 645.47 1669.2 645.47C1577.07 645.47 1502.72 570.68 1502.72 478.52Z"/>
          <path fill="#333" d="M1984.87 642.2V373.3H1881.98V314.85H2146.67V373.3H2047.53V642.2H1984.87Z"/>
          <path fill="#333" d="M2210.76 476.329C2212.19 384.479 2286.38 311.029 2378.23 311.569C2469.89 312.119 2543.71 386.73 2544.17 478.99C2544.63 571.25 2469.35 645.99 2377.22 645.99C2284.21 645.94 2209.31 569.679 2210.76 476.329ZM2481.04 478.99C2481.04 419.13 2437.04 369.99 2377.22 369.99C2317.83 369.99 2273.4 419.09 2273.4 478.99C2273.4 538.38 2317.4 586.99 2377.22 586.99C2437.04 586.99 2481.04 538.85 2481.04 478.99Z"/>
          <path fill="#333" d="M2629.76 642.2V314.85H2777.07C2841.61 314.85 2890.24 366.29 2890.24 425.68C2890.19 446.932 2883.61 467.656 2871.4 485.051C2859.19 502.447 2841.94 515.675 2821.97 522.95L2894.92 642.2H2823.37L2755.56 530.9H2692.93V642.2H2629.76ZM2692.9 476.2H2776.14C2806.07 476.2 2829.45 454.2 2829.45 423.83C2829.45 394.37 2807.45 371.45 2777.07 371.45H2692.93L2692.9 476.2Z"/>
          <path fill="#333" d="M3053.93 539.78L2940.29 314.85H3007.17L3084.8 468.7L3162.43 314.85H3229.3L3117.06 537.91V642.2H3053.93V539.78Z"/>
        </svg>
      </div>
      <div class="subtitle">DROID RECEIPT</div>
    </div>
    
    <div style="text-align: center;">
      <span class="model-badge">{model_name}</span>
    </div>
    
    <div class="meta">
      <div class="meta-row">
        <span class="meta-label">Location</span>
        <span class="meta-value">{location}</span>
      </div>
      <div class="meta-row">
        <span class="meta-label">Session</span>
        <span class="meta-value">{session_short}</span>
      </div>
      <div class="meta-row">
        <span class="meta-label">Date</span>
        <span class="meta-value">{date_str}</span>
      </div>
      <div class="meta-row">
        <span class="meta-label">Duration</span>
        <span class="meta-value">{duration_str}</span>
      </div>
    </div>
    
    <div class="separator"></div>
    
    <div class="items-header">
      <span>ITEM</span>
      <span>QTY</span>
      <span>PRICE</span>
    </div>
    
    <div class="item">
      <div class="item-row">
        <span class="item-label">Input tokens</span>
        <span class="qty">{format_number(input_tokens)}</span>
        <span class="price">{format_currency(input_tokens)}</span>
      </div>
      <div class="item-row">
        <span class="item-label">Output tokens</span>
        <span class="qty">{format_number(output_tokens)}</span>
        <span class="price">{format_currency(output_tokens)}</span>
      </div>'''
    
    if cache_write > 0:
        html += f'''
      <div class="item-row">
        <span class="item-label">Cache write</span>
        <span class="qty">{format_number(cache_write)}</span>
        <span class="price">{format_cache_currency(cache_write)}</span>
      </div>'''
    
    if cache_read > 0:
        html += f'''
      <div class="item-row">
        <span class="item-label">Cache read</span>
        <span class="qty">{format_number(cache_read)}</span>
        <span class="price">{format_cache_currency(cache_read)}</span>
      </div>'''
    
    html += f'''
    </div>
    
    <div class="total-section">
      <div class="total-row">
        <span>TOTAL</span>
        <span>{total_cost_str}</span>
      </div>
    </div>
    
    <div class="footer">
      <div class="cashier">SERVED BY: {droid_name}</div>
      <div class="thank-you">Thank you for building!</div>
      <div class="github-link">
        <a href="https://factory.ai" target="_blank">factory.ai</a>
      </div>
    </div>
  </div>
  
  <script>
    console.log('Droid Receipt Generated!');
    console.log('Session: {session_short}');
    console.log('Total: {total_cost_str}');
  </script>
</body>
</html>'''
    
    return html


def generate_svg(session_data: dict) -> str:
    """Generate SVG receipt from session data."""
    
    # Extract data
    session_id = session_data["session_id"]
    # Use short session ID (first 8 chars)
    session_short = session_id[:8] if len(session_id) >= 8 else session_id
    location = session_data.get("location", "The Cloud")[:30]
    model = session_data["model"]
    model_name = get_model_name(model)
    droid_name = generate_droid_name(session_id)
    tokens = session_data["tokens"]
    end_time = session_data.get("end_time", datetime.now().isoformat())
    active_time = session_data.get("active_time_ms", 0)
    
    # Calculate totals
    input_tokens = tokens.get("inputTokens", 0)
    output_tokens = tokens.get("outputTokens", 0)
    cache_write = tokens.get("cacheCreationTokens", 0)
    cache_read = tokens.get("cacheReadTokens", 0)
    total_tokens = input_tokens + output_tokens + cache_write + cache_read
    
    # Costs: regular tokens at $1/M, cache tokens at $0.10/M
    input_cost = format_currency(input_tokens)
    output_cost = format_currency(output_tokens)
    cache_write_cost = format_cache_currency(cache_write)
    cache_read_cost = format_cache_currency(cache_read)
    total_cost_val = (
        (input_tokens + output_tokens) / 1_000_000 * PRICE_PER_MILLION +
        (cache_write + cache_read) / 1_000_000 * PRICE_PER_MILLION * CACHE_PRICE_MULTIPLIER
    )
    total_cost = f"${total_cost_val:.2f}"
    
    # Format date
    try:
        dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        date_str = end_time
    
    # Format duration
    duration_str = format_duration(active_time)
    
    # Escape text for XML
    location = escape_xml(location)
    model_name = escape_xml(model_name)
    droid_name = escape_xml(droid_name)
    session_short = escape_xml(session_short)
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="580" viewBox="0 0 400 580" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .receipt-bg {{ fill: #f8f8f8; }}
      .text {{ font-family: 'Courier New', Courier, monospace; font-size: 12px; fill: #333; }}
      .text-bold {{ font-family: 'Courier New', Courier, monospace; font-size: 12px; fill: #333; font-weight: bold; }}
      .text-large {{ font-family: 'Courier New', Courier, monospace; font-size: 16px; fill: #333; font-weight: bold; }}
      .text-small {{ font-family: 'Courier New', Courier, monospace; font-size: 10px; fill: #666; }}
      .text-tiny {{ font-family: 'Courier New', Courier, monospace; font-size: 9px; fill: #999; }}
      .separator {{ stroke: #333; stroke-width: 2; }}
      .light-separator {{ stroke: #ccc; stroke-width: 1; stroke-dasharray: 2,2; }}
      .logo-text {{ font-family: Arial, sans-serif; font-size: 24px; fill: #333; font-weight: bold; }}
      .model-tag {{ fill: #e8e8e8; }}
    </style>
  </defs>
  
  <!-- Receipt background -->
  <rect class="receipt-bg" x="10" y="10" width="380" height="560" rx="4"/>
  
  <!-- Header -->
  <text x="200" y="55" class="logo-text" text-anchor="middle">FACTORY</text>
  <text x="200" y="78" class="text-small" text-anchor="middle">DROID RECEIPT</text>
  
  <!-- Separator -->
  <line x1="30" y1="95" x2="370" y2="95" class="separator"/>
  
  <!-- Model badge -->
  <rect class="model-tag" x="100" y="105" width="200" height="22" rx="3"/>
  <text x="200" y="121" class="text-bold" text-anchor="middle" font-size="11">{model_name}</text>
  
  <!-- Session info -->
  <text x="30" y="150" class="text">Location</text>
  <text x="370" y="150" class="text" text-anchor="end">{location}</text>
  <line x1="105" y1="146" x2="285" y2="146" class="light-separator"/>
  
  <text x="30" y="170" class="text">Session</text>
  <text x="370" y="170" class="text" text-anchor="end">{session_short}</text>
  <line x1="105" y1="166" x2="285" y2="166" class="light-separator"/>
  
  <text x="30" y="190" class="text">Date</text>
  <text x="370" y="190" class="text" text-anchor="end">{date_str}</text>
  <line x1="105" y1="186" x2="285" y2="186" class="light-separator"/>
  
  <text x="30" y="210" class="text">Duration</text>
  <text x="370" y="210" class="text" text-anchor="end">{duration_str}</text>
  <line x1="105" y1="206" x2="285" y2="206" class="light-separator"/>
  
  <!-- Separator -->
  <line x1="30" y1="230" x2="370" y2="230" class="separator"/>
  
  <!-- Header -->
  <text x="30" y="255" class="text-bold">ITEM</text>
  <text x="200" y="255" class="text-bold" text-anchor="middle">QTY</text>
  <text x="370" y="255" class="text-bold" text-anchor="end">PRICE</text>
  
  <line x1="30" y1="265" x2="370" y2="265" class="light-separator"/>
  
  <!-- Line items -->
  <text x="45" y="290" class="text">Input tokens</text>
  <text x="200" y="290" class="text" text-anchor="middle">{format_number(input_tokens)}</text>
  <text x="370" y="290" class="text" text-anchor="end">{input_cost}</text>
  
  <text x="45" y="310" class="text">Output tokens</text>
  <text x="200" y="310" class="text" text-anchor="middle">{format_number(output_tokens)}</text>
  <text x="370" y="310" class="text" text-anchor="end">{output_cost}</text>'''
    
    # Add cache tokens if present
    y_offset = 330
    if cache_write > 0:
        svg += f'''
  <text x="45" y="{y_offset}" class="text">Cache write</text>
  <text x="200" y="{y_offset}" class="text" text-anchor="middle">{format_number(cache_write)}</text>
  <text x="370" y="{y_offset}" class="text" text-anchor="end">{cache_write_cost}</text>'''
        y_offset += 20
    
    if cache_read > 0:
        svg += f'''
  <text x="45" y="{y_offset}" class="text">Cache read</text>
  <text x="200" y="{y_offset}" class="text" text-anchor="middle">{format_number(cache_read)}</text>
  <text x="370" y="{y_offset}" class="text" text-anchor="end">{cache_read_cost}</text>'''
        y_offset += 20
    
    # Total section
    total_y = y_offset + 15
    
    svg += f'''
  
  <!-- Total section -->
  <line x1="30" y1="{total_y}" x2="370" y2="{total_y}" class="separator"/>
  
  <text x="30" y="{total_y + 25}" class="text-bold" font-size="14">TOTAL</text>
  <text x="370" y="{total_y + 25}" class="text-bold" font-size="14" text-anchor="end">{total_cost}</text>
  
  <line x1="30" y1="{total_y + 40}" x2="370" y2="{total_y + 40}" class="separator"/>
  
  <!-- Footer -->
  <text x="200" y="{total_y + 70}" class="text" text-anchor="middle">SERVED BY: {droid_name}</text>
  
  <text x="200" y="{total_y + 100}" class="text" text-anchor="middle">Thank you for building!</text>
  
  <line x1="100" y1="{total_y + 120}" x2="300" y2="{total_y + 120}" class="light-separator"/>
  
  <text x="200" y="{total_y + 140}" class="text-small" text-anchor="middle">factory.ai</text>
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
        
        # Parse transcript for end time
        end_time = datetime.now().isoformat()
        
        if os.path.exists(transcript_path):
            with open(transcript_path, "r") as f:
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
            "location": location,
            "model": model,
            "tokens": tokens,
            "end_time": end_time,
            "active_time_ms": active_time_ms,
        }
        
        # Create output directory
        RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Determine output format from env or default to both
        output_format = os.environ.get("DROID_RECEIPT_FORMAT", "html").lower()
        
        # Generate and save receipts
        opened_path = None
        
        if output_format in ("html", "both"):
            html_content = generate_html(session_data)
            html_path = RECEIPTS_DIR / f"{session_id}.html"
            with open(html_path, "w") as f:
                f.write(html_content)
            print(f"HTML receipt saved to {html_path}")
            opened_path = html_path
        
        if output_format in ("svg", "both"):
            svg_content = generate_svg(session_data)
            svg_path = RECEIPTS_DIR / f"{session_id}.svg"
            with open(svg_path, "w") as f:
                f.write(svg_content)
            print(f"SVG receipt saved to {svg_path}")
            if not opened_path:
                opened_path = svg_path
        
        # Open in browser (macOS)
        if opened_path and sys.platform == "darwin":
            os.system(f'open "{opened_path}"')
        
    except Exception as e:
        print(f"Error generating receipt: {e}", file=sys.stderr)
        sys.exit(0)  # Non-blocking exit


if __name__ == "__main__":
    main()

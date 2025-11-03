"""
Website Widget Service
Embeddable AI chat widget for client websites
"""

import hashlib
import secrets
from django.conf import settings


class WidgetService:
    """
    Service for managing website chat widget
    """

    # Widget themes with color presets
    THEMES = {
        'light': {
            'name': 'Light',
            'primary': '#3B82F6',      # Blue
            'background': '#FFFFFF',
            'text': '#1F2937',
            'headerBg': '#3B82F6',
            'headerText': '#FFFFFF',
            'userBubble': '#3B82F6',
            'userText': '#FFFFFF',
            'botBubble': '#F3F4F6',
            'botText': '#1F2937',
        },
        'dark': {
            'name': 'Dark',
            'primary': '#8B5CF6',      # Purple
            'background': '#1F2937',
            'text': '#F9FAFB',
            'headerBg': '#111827',
            'headerText': '#F9FAFB',
            'userBubble': '#8B5CF6',
            'userText': '#FFFFFF',
            'botBubble': '#374151',
            'botText': '#F9FAFB',
        },
        'brand': {
            'name': 'Brand Colors',
            'primary': '#EC4899',      # Pink (салони краси)
            'background': '#FFFFFF',
            'text': '#1F2937',
            'headerBg': '#EC4899',
            'headerText': '#FFFFFF',
            'userBubble': '#EC4899',
            'userText': '#FFFFFF',
            'botBubble': '#FCE7F3',
            'botText': '#831843',
        }
    }

    @staticmethod
    def generate_widget_key(organization_id):
        """
        Generate unique widget API key for organization
        """
        random_string = f"{organization_id}-{secrets.token_urlsafe(32)}"
        return hashlib.sha256(random_string.encode()).hexdigest()

    @staticmethod
    def get_widget_config(integration):
        """
        Get widget configuration from integration

        Returns:
            dict: Widget configuration
        """
        config = integration.config or {}

        theme = config.get('theme', 'light')
        custom_colors = config.get('custom_colors', {})

        # Get theme colors or custom
        if custom_colors:
            colors = custom_colors
        else:
            colors = WidgetService.THEMES.get(theme, WidgetService.THEMES['light'])

        return {
            'widget_key': config.get('widget_key'),
            'theme': theme,
            'colors': colors,
            'position': config.get('position', 'bottom-right'),  # bottom-right, bottom-left
            'welcome_message': config.get('welcome_message', 'Привіт! Як я можу допомогти?'),
            'placeholder': config.get('placeholder', 'Напишіть повідомлення...'),
            'icon_url': config.get('icon_url', None),
            'show_branding': config.get('show_branding', True),
            'auto_open': config.get('auto_open', False),
            'auto_open_delay': config.get('auto_open_delay', 3000),  # ms
        }

    @staticmethod
    def generate_embed_code(widget_key, backend_url):
        """
        Generate JavaScript embed code for website

        Args:
            widget_key: Unique widget API key
            backend_url: Backend URL (e.g., https://api.sloth.ai)

        Returns:
            str: JavaScript code to embed
        """

        embed_code = f"""<!-- Sloth AI Chat Widget -->
<script>
  (function() {{
    window.SlothWidget = {{
      key: '{widget_key}',
      apiUrl: '{backend_url}'
    }};

    var script = document.createElement('script');
    script.src = '{backend_url}/static/widget/sloth-widget.js';
    script.async = true;
    document.head.appendChild(script);

    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '{backend_url}/static/widget/sloth-widget.css';
    document.head.appendChild(link);
  }})();
</script>
<!-- End Sloth AI Chat Widget -->"""

        return embed_code

    @staticmethod
    def generate_widget_html(config):
        """
        Generate widget HTML structure (for preview)
        """
        colors = config['colors']

        html = f"""
<div id="sloth-widget" style="position: fixed; {config['position'].replace('-', ': 20px; ')}: 20px; z-index: 9999;">
  <!-- Widget Button -->
  <button id="sloth-widget-button" style="
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: {colors['primary']};
    border: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  ">
    {f'<img src="{config["icon_url"]}" style="width: 32px; height: 32px; border-radius: 50%;" />' if config.get('icon_url') else '<svg width="32" height="32" viewBox="0 0 24 24" fill="white"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>'}
  </button>

  <!-- Chat Window -->
  <div id="sloth-chat-window" style="
    width: 380px;
    height: 600px;
    background: {colors['background']};
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    display: none;
    flex-direction: column;
    overflow: hidden;
    margin-bottom: 80px;
  ">
    <!-- Header -->
    <div style="
      background: {colors['headerBg']};
      color: {colors['headerText']};
      padding: 16px;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: space-between;
    ">
      <span>AI Консультант</span>
      <button style="background: none; border: none; color: {colors['headerText']}; cursor: pointer;">✕</button>
    </div>

    <!-- Messages -->
    <div style="
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      background: {colors['background']};
    ">
      <div style="
        background: {colors['botBubble']};
        color: {colors['botText']};
        padding: 12px 16px;
        border-radius: 12px;
        max-width: 80%;
        margin-bottom: 8px;
      ">
        {config['welcome_message']}
      </div>
    </div>

    <!-- Input -->
    <div style="
      padding: 16px;
      border-top: 1px solid rgba(0,0,0,0.1);
      background: {colors['background']};
    ">
      <input type="text" placeholder="{config['placeholder']}" style="
        width: 100%;
        padding: 12px;
        border: 1px solid rgba(0,0,0,0.1);
        border-radius: 8px;
        color: {colors['text']};
        background: {colors['background']};
      " />
    </div>

    {f'<div style="padding: 8px; text-align: center; font-size: 11px; color: rgba(0,0,0,0.4);">Powered by Sloth AI</div>' if config.get('show_branding') else ''}
  </div>
</div>
"""
        return html

    @staticmethod
    def validate_widget_key(widget_key):
        """
        Validate widget key and return integration

        Returns:
            Integration or None
        """
        from apps.integrations.models import Integration

        try:
            integration = Integration.objects.get(
                integration_type='website_widget',
                is_active=True,
                config__widget_key=widget_key
            )
            return integration
        except Integration.DoesNotExist:
            return None

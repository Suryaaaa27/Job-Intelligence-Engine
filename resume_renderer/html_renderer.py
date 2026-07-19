from jinja2 import Environment, FileSystemLoader
import os

def render_html(data: dict, template_name: str = "general.html") -> str:
    """
    Renders the normalized resume data into an HTML string using the specified Jinja2 template.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(current_dir, "templates")
    
    if not os.path.exists(templates_dir):
        raise FileNotFoundError(f"Templates directory not found at {templates_dir}")
        
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    try:
        template = env.get_template(template_name)
    except Exception as e:
        raise ValueError(f"Could not load template '{template_name}': {e}")
        
    rendered_html = template.render(**data)
    return rendered_html

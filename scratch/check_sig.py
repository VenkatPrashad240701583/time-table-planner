from fastapi.templating import Jinja2Templates
import inspect

templates = Jinja2Templates(directory="templates")
print(inspect.signature(templates.TemplateResponse))

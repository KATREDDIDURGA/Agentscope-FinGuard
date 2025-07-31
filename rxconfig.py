import reflex as rx

class FinguradagentsConfig(rx.Config):
    pass

config = FinguradagentsConfig(
    app_name="", # This is correct: it points to the 'app.ui' Python package
    db_url="sqlite:///reflex.db", # Reflex's internal DB, separate from your app's fin_guard.db
    env="dev",
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    # api_url="http://localhost:8000" # Uncomment if your backend is on a different host/port
)

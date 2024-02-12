from os import getenv
from supabase import create_client, Client

# from supabase.lib.client_options import ClientOptions

url: str = getenv("SUPABASE_URL")
key: str = getenv("SUPABASE_SERVICE_ROLE")
# service_role: str = getenv("SUPABASE_SERVICE_ROLE")
# clientOptions = ClientOptions(headers={"Authorization": f"Bearer {service_role}"})
supa_client: Client = create_client(
    url,
    key,
    # clientOptions,
)

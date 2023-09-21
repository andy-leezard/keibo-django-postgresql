def generate_urls(is_local, base_url, pathnames):
    # Ensure the base_url ends with a '/'
    if not base_url.endswith('/'):
        base_url += '/'

    # Create URL based on the prod flag
    if is_local:
        prefix = "http://"
        urls = [prefix + base_url + pathname for pathname in pathnames]
    else:
        prefix_with_www = "https://www."
        prefix_without_www = "https://"
        # Use list comprehension to generate URLs with and without 'www.'
        urls_with_www = [
            prefix_with_www + base_url + pathname for pathname in pathnames
        ]
        urls_without_www = [
            prefix_without_www + base_url + pathname for pathname in pathnames
        ]
        urls = urls_without_www + urls_with_www

    return urls

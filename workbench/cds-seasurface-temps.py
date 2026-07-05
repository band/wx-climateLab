from ecmwf.datastores import Client

client = Client()
result = client.check_authentication()
print(f"auth check result: {result}")

collection_id = "satellite-sea-surface-temperature"

request = {
    "variable": "all",
    "processinglevel": "level_4",
    "sensor_on_satellite": "combined_product",
    "version": "3_0",
    "temporal_resolution": "monthly",
    "year": [
        "2016", "2017", "2018",
        "2019", "2020", "2021",
        "2022", "2023", "2024",
        "2025", "2026"
    ],
    "month": [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12"
    ],
    "data_format":"zip",
    "download_format":"archived",
}

client.retrieve(collection_id, request, target="seasurface_1.zip")


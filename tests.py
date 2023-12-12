import requests
USER_ID = ''
API_KEY = ''

def publish_metric(rom, temp):
    body = 'compost_temp,rom={},source=compost-esp metric={}'.format(rom, temp)
    print(body)

    max_retries = 6
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = requests.post(
                'http://influx-prod-09-prod-au-southeast-0.grafana.net/api/v1/push/influx/write',
                headers={
                    'Content-Type': 'text/plain',
                },
                data=str(body),
                auth=(USER_ID, API_KEY)
            )

            status_code = response.status_code
            print(status_code)
            if status_code == 204:  # Successful response
                break
            else:
                print(f"Failed to publish metric. Status code: {status_code}")
        except Exception as e:
            print(f"Error: {e}")

        retry_count += 1
        time.sleep(1)  # Wait for a short duration before retrying

publish_metric("test", 10)
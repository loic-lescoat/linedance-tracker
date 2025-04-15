# Track your line-dance progress!

## Usage

```
make build
make run
```

## Optional: auto-update list of line dances

Add the following to your `crontab`:

```
0 0 * * * container_id=`docker ps | grep linedance | awk '{ print $1 }'` docker exec -it $container_id python3 ./update.py

```

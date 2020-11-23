#! /bin/sh
while IFS= read -r URL; do
	scrapy crawl nosetime -a "$URL"
done

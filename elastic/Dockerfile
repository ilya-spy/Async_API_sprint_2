FROM elasticsearch:8.1.3 as init-indices

COPY schemas /schemas
COPY init-indices.sh /init-indices.sh

RUN elasticsearch -d -p pid -E path.data=/tmp/data -E discovery.type=single-node -E xpack.security.enabled=false \
    && while [[ "$(curl -s -o /dev/null -w '%{http_code}' localhost:9200)" != "200" ]]; do sleep 1; done \
    && bash /init-indices.sh

FROM elasticsearch:8.1.3
COPY --from=init-indices /tmp/data/ /usr/share/elasticsearch/data/
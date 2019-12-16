


# Build Container

FROM alpine:3.10 as build

ADD dev-packages.txt /packages.txt
RUN xargs apk --no-cache add < /packages.txt \
  && pip3 install --upgrade pip && pip3 install wheel \
  && mkdir /build && mkdir /wheelhouse

WORKDIR /build

ADD requirements.txt requirements.txt
ADD setup.py setup.py
ADD src src

RUN pip3 wheel -w /wheelhouse . \
  && pip3 wheel -w /wheelhouse uwsgi



# Runtime Container

FROM alpine:3.10 as runtime

ENV HOST=0.0.0.0
ENV PORT=8080
ENV UWSGI_MODULE=demo_app_iam_service:app
ENV WORKER_PROCESSES=4

COPY --from=build /wheelhouse /wheelhouse
ADD start.sh /usr/local/bin/start.sh
ADD packages.txt /packages.txt

RUN xargs apk --no-cache add < /packages.txt \
  && pip3 install --upgrade pip \
  && pip3 install -f /wheelhouse/ demo_app_iam_service uwsgi \
  && adduser --system demo_app --home /tmp

USER demo_app
WORKDIR /tmp

ENTRYPOINT []
CMD ["start.sh"]

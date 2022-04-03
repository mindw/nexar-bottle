FROM python:3.10-alpine3.15
# switch to alpine for a something slimmer.
# another option is https://github.com/GoogleContainerTools/distroless 
#FROM python:3.10-slim-bullseye

#ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=0

# disable writing bytecode
ENV PYTHONDONTWRITEBYTECODE=1
ENV LANG C.UTF-8
ENV USER=search
ENV ID=19733

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
# don't cache and don't create bytecode
RUN pip install --no-cache-dir --no-compile --upgrade -r /app/requirements.txt

RUN set -ex; \
    addgroup --gid ${ID} ${USER}; \
    adduser --ingroup ${USER} --uid ${ID} --gecos "" --disabled-password --no-create-home ${USER}; \
    chown -R ${USER}:${USER} /app

COPY samples /data
COPY src /app

USER ${ID}:${ID}

EXPOSE 8080
ENTRYPOINT [ "python3" ]
CMD [ "__init__.py", "/data" ]

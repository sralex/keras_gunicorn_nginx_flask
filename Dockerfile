FROM continuumio/miniconda3

ENV APP_ROOT /src
ENV CONFIG_ROOT /config


RUN mkdir ${CONFIG_ROOT}
COPY /app/environment.yml ${CONFIG_ROOT}/environment.yml
RUN /opt/conda/bin/conda env create -f ${CONFIG_ROOT}/environment.yml


SHELL ["conda", "run", "-n", "keras_gunicorn_nginx_flask", "/bin/bash", "-c"]


RUN mkdir ${APP_ROOT}
WORKDIR ${APP_ROOT}

ADD /app/ ${APP_ROOT}

ENTRYPOINT ["conda", "run", "-n", "keras_gunicorn_nginx_flask", "gunicorn","--workers=2", "--bind=0.0.0.0:8000","main:app"]

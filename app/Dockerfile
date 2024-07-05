###########
# BUILDER #
###########

FROM python:3.12 as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends gcc

RUN pip install -U pip
COPY . /app/

COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


#########
# FINAL #
#########

FROM python:3.12

RUN mkdir -p /home/app

RUN addgroup --system app && adduser --system --group app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
ENV PYTHONPATH "${PYTHONPATH}:/home/app/web"
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y --no-install-recommends netcat-traditional nano
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install -U pip
RUN pip install --no-cache /wheels/*

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh

COPY . $APP_HOME

RUN chown -R app:app $APP_HOME

USER app

ENTRYPOINT ["/home/app/web/entrypoint.sh"]
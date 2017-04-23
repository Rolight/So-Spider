#!/bin/bash
check_non_empty() {
  # $1 is the content of the variable in quotes e.g. "$FROM_EMAIL"
  # $2 is the error message
  if [[ "$1" == "" ]]; then
    echo "ERROR: specify $2"
    exit -1
  fi
}


check_exec_success() {
  # $1 is the content of the variable in quotes e.g. "$FROM_EMAIL"
  # $2 is the error message
  if [[ "$1" != "0" ]]; then
    echo "ERROR: $2 failed"
    echo "$3"
    exit -1
  fi
}

CurDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

create_data_volume(){
  docker inspect so-spider-data &> /dev/null
  if [[ "$?" == "1" ]]; then
    docker create --name so-spider-data \
      -v ${CurDir}:/usr/src/app \
      alpine /bin/true

    docker run --rm --volumes-from so-spider-data \
      ${BaseImage} mkdir -p logs/uwsgi/ logs/cron/
  fi

}

start() {
  spider_name="so-spider-$1"
  echo $spider_name
  docker kill so-dashboard 2>/dev/null
  docker rm -v so-dashboard 2>/dev/null

  create_data_volume

  docker run -d --name so-dashboard \
    -e "DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}" \
    -p 8081:8081 \
    --volumes-from so-dashboard-data \
    --restart=always \
    --log-opt max-size=10m \
    --log-opt max-file=9 \
    ${BaseImage} \
    uwsgi --ini /usr/src/app/dashboard/uwsgi.ini -b 99999

  check_exec_success "$?" "start so-dashboard container"
}

BaseImage=""

##################
# Start of script
##################

Action=$1

shift

case "$Action" in
  start) start "$@";;
  stop) stop ;;
  *)
    echo "Usage:"
    echo "./start.sh start|stop"
    exit 1
    ;;
esac

exit 0

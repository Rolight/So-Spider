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
LogDir=/data/so-spider/log/
BaseImage="daocloud.io/rolight/so-spider:feature-scheduler-b732c3c"

mkdir -p $LogDir

create_data_volume(){
  docker inspect so-spider-data &> /dev/null
  if [[ "$?" == "1" ]]; then
    docker create --name so-spider-data \
      -v ${CurDir}:/usr/src/app \
      -v ${LogDir}:/usr/src/app/logs \
      alpine /bin/true

    docker run --rm --volumes-from so-spider-data \
      ${BaseImage} mkdir -p logs/uwsgi/ logs/cron/
  fi

}

start() {
  spider_name="so-spider-$1"
  echo $spider_name

  docker kill "$spider_name" 2>/dev/null
  docker rm -v "$spider_name" 2>/dev/null

  create_data_volume

  docker run -d --name $spider_name \
    --volumes-from so-spider-data \
    ${BaseImage} \
    python scheduler.py "$1"

  check_exec_success "$?" "start spider $1 container"
}

shell() {
  create_data_volume

  docker run -it --rm \
    --volumes-from so-spider-data \
    ${BaseImage} \
    bash
}

stop() {
  spider_name="so-spider-$1"
  docker stop $spider_name 2>/dev/null
  docker rm -v $spider_name 2>/dev/null
  docker rm -v $spider_name 2>/dev/null
}


##################
# Start of script
##################

Action=$1

shift

case "$Action" in
  start) start "$@";;
  stop) stop "$@";;
  shell) shell ;;
  *)
    echo "Usage:"
    echo "./start.sh start|stop"
    echo "./start.sh shell"
    exit 1
    ;;
esac

exit 0

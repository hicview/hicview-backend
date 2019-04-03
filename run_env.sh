#!/bin/bash
# saner programming env: these switches turn some bugs into errors
set -o errexit -o pipefail -o noclobber -o nounset

! getopt --test > /dev/null 
if [[ ${PIPESTATUS[0]} -ne 4 ]]; then
    echo 'I’m sorry, `getopt --test` failed in this environment.'
    echo 'If you are using Mac OSX:'
    echo 'Install gnu-getopt using:'
    echo '    brew install gnu-getopt'
    echo "    echo 'export PATH=\"/usr/local/opt/gnu-getopt/bin:\$PATH\"' >> ~/.profile"
    exit 1
fi

OPTIONS=:armscvhz
LONGOPTS=debug,force,output:,verbose

# -use ! and PIPESTATUS to get exit code with errexit set
# -temporarily store output to be able to check for errors
# -activate quoting/enhanced mode (e.g. by writing out “--options”)
# -pass arguments only via   -- "$@"   to separate them correctly
! PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
    # e.g. return value is 1
    #  then getopt has complained about wrong arguments to stdout
    exit 2
fi

echo $PARSED
# read getopt’s output this way to handle the quoting right:
eval set -- "$PARSED"


n="n" y="y"

mongodb=$n mysqldb=$n redisdb=$n
verbose=$n clear_docker=$y help=$n
remove_container=$n
# f=$n d=$n v=$n outFile=$n
# now enjoy the options in order and nicely split until we see --
while true; do
    case "$1" in
	-a|--all)
	    mongodb=$y
	    mysqldb=$y
	    redisdb=$y
	    shift
	    ;;	
        -r|--redis)
            redisdb=$y
            shift
            ;;
        -m|--mongo)
	    mongodb=$y
            shift
            ;;
	-s|--mysql)
	    mysqldb=$y
	    shift
	    ;;
	-c|--noclear)
	    clear_docker=$n
	    shift
	    ;;
	-z|--remove)
	    remove_container=$y
	    shift
	    ;;
        -v|--verbose)
            verbose=$y
            shift
            ;;
	-h|--help)
	    help=$y
	    shift
	    ;;
#        -o|--output)
#            outFile="$2"
#            shift 2
#            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Programming error"
            exit 3
            ;;
    esac
done

function Help(){
    echo "-a|--all run mysql, redis and mongodb docker"
    echo "-s|--mysql"
    echo "-m|--mongodb"
    echo "-r|--redis"
    echo "-v|--verbose"
    echo "-c|--noclear"
    echo "-h|--help"
    echo "-z|--remove"
}

echo "$#"



if [ $help == y ]; then
    Help
    exit 0
fi
   

# handle non-option arguments
if [[ $# == 0 && $help == "n" && $mongodb == "n" \
    && $mysqldb == "n" && $redisdb == "n" && $remove_container == "n" ]] ; then
    echo "$0: Help information."
    Help
    exit 0
fi

if [[ $remove_container == y ]]; then
    redis_container=$(docker ps -a --filter "name=redis_container" -q)
    docker stop $redis_container && docker rm -v $redis_container
    mongo_container=$(docker ps -a --filter "name=mongo_container" -q)
    docker stop $mongo_container && docker rm -v $mongo_container
    mysql_container=$(docker ps -a --filter "name=mysql_container" -q)
    docker stop $mysql_container && docker rm -v $mysql_container
    exit 0
fi


if [[ $clear_docker == y ]]; then
    redis_container=$(docker ps -a --filter "name=redis_container" -q)
    docker stop $redis_container && docker rm -v $redis_container
    mongo_container=$(docker ps -a --filter "name=mongo_container" -q)
    docker stop $mongo_container && docker rm -v $mongo_container
    mysql_container=$(docker ps -a --filter "name=mysql_container" -q)
    docker stop $mysql_container && docker rm -v $mysql_container    
fi

if [[ $mysqldb == y ]]; then
    docker run \
	   -p 3306:3306 \
	   --name=mysql_container \
	   -v $PWD/env/mysql_data/db:/var/lib/mysql \
	   -e MYSQL_ROOT_PASSWORD="test123" \
	   -d mysql:5.6
fi

if [[ $mongodb == y ]]; then
    docker run \
       -p 27017:27017 \
       --name mongo_container \
       -v $PWD/env/mongo_data/db:/data/db \
       -d mongo:4.0

    echo "MongoDB container started"
    
fi

if [[ $redisdb == y ]]; then
    docker run \
       -p 6379:6379 \
       -v $PWD/env/redis_data:/data:rw \
       --name redis_container \
       -d redis:5.0 redis-server --appendonly yes
    echo "Redis container started"       
fi


echo "mongodb:$mongodb mysqldb:$mysqldb redisdb=$redisdb verbose=$verbose \
clear_docker=$clear_docker"



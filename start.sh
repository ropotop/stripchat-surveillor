while true
do
	python3 surveillor.py -l & pid=$!
	sleep 30
	kill "$pid"
	sleep 5
done

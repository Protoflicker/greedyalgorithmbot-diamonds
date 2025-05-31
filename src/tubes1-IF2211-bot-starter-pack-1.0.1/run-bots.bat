@echo off
start cmd /c "python main.py --logic original --email=test_ori1@gmail.com --name=ori1 --password=123456 --team=etimo"
start cmd /c "python main.py --logic greedyred --email=test_greedy72@gmail.com --name=greedyred1 --password=123456 --team=etimo"
start cmd /c "python main.py --logic greedy12 --email=test_greedy12s@gmail.com --name=greedy12s --password=123456 --team=etimo"
start cmd /c "python main.py --logic mybot --email=test_astar1@gmail.com --name=astar1 --password=123456 --team=etimo"
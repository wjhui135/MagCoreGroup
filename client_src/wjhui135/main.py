from client_src.wjhui135 import function
import threading

#传入一个坐标，获取某个单元周围的坐标，返回坐标列表
def GetAround(xy):
    list_re = []
    if xy[0] > 0:
        left = [xy[0]-1,xy[1]]
        list_re.append(left)

    right = [xy[0]+1,xy[1]]
    list_re.append(right)

    if xy[1] > 0:
        up = [xy[0],xy[1]-1]
        list_re.append(up)

    down = [xy[0],xy[1]+1]
    list_re.append(down)
    return list_re

#传入已属于自己的单元的坐标列表，获取攻击范围，包括领地四周单元+已属于自己的单元
def GetCell(list_own):
    list_re = list_own[:]
    for cell in list_own:
        list_re.extend(GetAround(cell))
    list_set = []
    for i in list_re:
        if i not in list_set:
            list_set.append(i)
    return list_set

#封装游戏准备部分的代码，从创建游戏（加入游戏）到开始游戏
def GameReady():
    choice = input("请问你需要新建游戏吗？(Y/N):")
    while True:
        if choice == 'Y' or choice == 'y':#新建游戏
            map_style = input("请输入地图种类(RectSmall/RectMid/RectLarge)：")
            while True:
                if map_style.lower() not in ['rectsmall','rectmid','rectlarge']:
                    map_style = input("输入错误！请重新输入(RectSmall/RectMid/RectLarge)：")
                else:
                    break
            gameID = function.CreateGame(map_style)
            print("创建成功！您创建的游戏的ID为：" + gameID)
            break
        elif choice == 'N' or choice == 'n':#加入游戏
            gameID = input("若要加入游戏，请输入游戏ID：")
            break
        else:
            choice = input("输入错误！请重新输入：")
            continue
    print("在加入游戏前，请您输入必要的信息")
    while True:
        player_name = input("请输入您的昵称：")
        player_color = input("请选择您想使用的颜色代码(0: ⾹蕉/1: 樱桃/2: 葡萄/3: 菜⽠/4: 柠檬/5: 桑葚/6: ⽣梨/7: 菠萝/8: 萝⼘/9: ⻄⽠)：")
        player = function.CreatPlayer(player_name,int(player_color))
        if player == None:
            print("玩家昵称已存在，请重新输入！")
            continue
        result = function.JoinGame(gameID, player["Id"])
        if result:
            print("加入游戏成功！您的游戏昵称为%s，颜色为%s，id为%s,index为%s" % (player['Name'],player['Color'],player['Id'],player['Index']))
            break
        else:
            print("玩家颜色已存在，请重新输入！")
    first = True
    num = 100
    while True:
        game_detail = function.GetGame(gameID)
        if game_detail['State'] != 0:
            break
        player_num = len(game_detail['Players'])
        if player_num < 2 and first:
            print("当前人数少于2人，等待玩家加入...")
        elif player_num != num or first:
            choice = input("已加入游戏人数为%d，是否开始游戏？(Y/N):" % player_num)
            if choice == 'Y' or choice == 'y':
                result = function.StartGame(gameID)
                if result:
                    print("游戏开始！")
                break
        num = player_num
        first = False
    print("战斗吧！")
    game_info = {}
    game_info['gameId'] = gameID
    game_info['playerId'] = player['Id']
    return game_info

#封装攻击部分的代码
def AttackCell(game_detail,player_detail):
    list_own = []
    for tmp in game_detail['Cells']:
        for i in tmp:
            if int(i['Owner']) == int(player_detail['Index']):
                list_own.append([i['X'], i['Y']])
    list_cell = GetCell(list_own)
    print("战场瞬息万变，争分夺秒很关键！")
    print("当前可攻击的单元有：")
    count = 1
    for cell in list_cell:
        for tmp in game_detail['Cells']:
            for i in tmp:
                if int(i['X']) == int(cell[0]) and int(i['Y']) == int(cell[1]):
                    print("%d.坐标：%d,%d；类型：%d；状态：%d；拥有者：%d"
                          % (count, i['X'], i['Y'], i['Type'], i['State'], i['Owner']))
                    count += 1
    cell_index = int(input("请选择要攻击的单元，输入其序号："))
    result = function.Attack(game_detail['Id'], player_detail["Id"], list_cell[cell_index - 1][0], list_cell[cell_index - 1][1])
    return result

#判断游戏中是否还有玩家的领地
def isNotInGame(player_index,game_detail):
    for tmp in game_detail['Cells']:
        for i in tmp:
            if i['Owner'] == player_index:
                return False
    return True

#判断玩家是否为游戏中唯一的幸存者，即胜利者
def isOnlyInGame(player_index,game_detail):
    for tmp in game_detail['Cells']:
        for i in tmp:
            if i['Owner'] != 0 and i['Owner'] != player_index:
                return False
    return True

if __name__ == '__main__':
    ##############################游戏准备阶段################################
    print("欢迎来到磁芯大战！当前游戏列表如下：\n%-40s %-20s state" % ("gameid","map"))
    gameList = function.GetGameList()
    for game in gameList:
        print("%-40s %-20s " % (game["id"],game["map"]) + str(game["state"]))
    game_info = GameReady()  #返回游戏id和当前玩家的id，字典类型
    ##############################游戏战斗阶段#################################
    playerId = game_info['playerId']
    gameId = game_info['gameId']
    # playerId = 'e5a459a9dc1841c080ea76f83a741323'
    # gameId = 'aef4aa50562e4f428149b6183bf7f3f7'
    first = True
    tmp_detail = {}
    while True:
        player_detail = function.GetPlayer(playerId)
        game_detail = function.GetGame(gameId)
        if isNotInGame(player_detail["Index"],game_detail):
            print("Defeat!")
            break
        if isOnlyInGame(player_detail["Index"],game_detail):
            print("Win!")
            break
        # AttackCell(game_detail,player_detail)
        # #将AttackCell函数的调用放到子线程，与主线程同时进行
        if game_detail != tmp_detail or first:
            t1 = threading.Thread(target=AttackCell,args=(game_detail,player_detail))
            t1.setDaemon(True)
            t1.start()
            first = False
        tmp_detail = game_detail
        '''
        需要考虑的问题：
        战斗的时候，如果攻击的是自己的单位会怎么样？
        攻击对方的单位会怎么样？
        攻击空白单位会怎么样？
        '''
    print("game over!")
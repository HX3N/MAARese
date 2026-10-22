# tutorial/level/guide_01_b
trigger: 없음

1. (전투) Battle.Pause
2. [아미야] 쓰러뜨려야 하는 적이 나타났어요! — anim=Highlight
3. [아미야] 저 '리유니온'의 폭도들을 쓰러뜨리지 않으면 성가신 일이 벌어지겠죠… — anim=Highlight
4. (전투) Battle.UnlockFunction(mask=CARD_LIST)
5. [아미야] 아래에 표시된 건 로도스 아일랜드의 오퍼레이터들입니다. — anim=Highlight
6. [아미야] 오퍼레이터를 전장에 배치하면 바로 작전에 참여할 수 있게 돼요. — anim=Highlight
7. (전투) Battle.UnlockFunction(mask=COST_PANEL)
8. [아미야] 오퍼레이터 리스트 위에 표시된 숫자는 현재 보유 중인 배치 코스트에요. — anim=Highlight, target=panel_cost
9. [아미야] 오퍼레이터를 전장에 배치할 땐 이 코스트를 쓰게 되죠. — anim=Highlight, target=panel_cost
10. [아미야] 오퍼레이터 아이콘 상단에는 각자 다른 숫자가 표시되어 있는데, 이건 오퍼레이터를 배치할 때 필요한 배치 코스트에요. — anim=Highlight
11. [아미야] 일반적으로는 강력한 오퍼레이터일수록 배치 코스트가 높아지는 경향이 있으니 참고해주세요.
12. [아미야] 하지만 보유 코스트는 시간이 지남에 따라 회복되니 걱정하실 필욘 없어요.
13. [아미야] 박사님, 손가락의 감각이 이제 돌아왔을 거예요.
14. [아미야] 손가락에 감각을 집중시켜보도록 하죠, 어느 손가락이든 상관없어요.
15. (전투) Battle.EnsureMinCost(cost=11)
16. [아미야] 제가 가리키는 위치가 보이신다면, 오퍼레이터를 여기까지 이동시켜 보시겠어요? — anim=Drag, signal=put_down
17. [아미야] 그리고 중앙에 있는 방향 지시 아이콘을 이쪽 방향으로 드래그해주세요. — anim=Drag, signal=select_direction
18. (전투) Battle.Pause(pause=false)
19. (전투) Battle.Pause(pause=true)
20. [아미야] 이제 저 적은 방금 배치한 오퍼레이터, 텍사스 씨에게 맡겨보도록 하죠.

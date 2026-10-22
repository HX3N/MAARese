# guide/l0-0/1_recruit_adv
trigger: STORY_FINISH_OR_PAGE_LOADED obt/guide/l0-0/0_home_ui|home

1. [PRTS] 기억 상실의 영향이 예상보다 큰 것 같습니다.
2. [PRTS] 하지만 이곳에서의 기본적인 행동 양식은 전부 파악하신 것 같습니다. 박사님을 구출하기 위해 노력한 아미야 님과 다른 오퍼레이터들도 기뻐하겠군요.
3. [아미야] 무엇보다 리유니온이 벌이는 파괴 활동이나, 그들이 우리에게 미치는 영향력은… 저희의 상상을 훨씬 뛰어넘고 있어요. 박사님, 이제부터 잘 헤쳐나가셔야 해요.
4. [PRTS] 살아남기 위해서는 로도스 아일랜드의 규모를 확대해 나가야만 합니다.
5. [아미야] 박사님, 오퍼레이터 후보의 프로필이 꽤 많이 도착했어요. 이 중에서 새로운 동료로 포섭할 수 있는 분도 분명 있을 거예요. 함께 찾아보도록 하죠.
6. [아미야] 박사님, '헤드헌팅'을 터치해 주세요. — anim=Highlight, target=btn_advanced_recruit
7. [PRTS] 여기에선 합성옥을 사용하여 오퍼레이터 헤드헌팅을 진행하실 수 있습니다.
8. [PRTS] 합성옥은 아주 귀중하며, 헤드헌팅을 할 때 꼭 필요한 자원이기도 합니다. 헤드헌팅을 진행하기에 앞서 정말 필요한 작업인지 신중하게 고려하여 주십시오. — anim=Highlight, target=panel_diamond_shard
9. [PRTS] 우선은 한번 진행해 보도록 하겠습니다. 이곳을 터치해 주십시오. — anim=Click, target=btn_gacha, signal=recruit_gacha_drawn
10. (대기) signal=recruit_gachaeffect_shown

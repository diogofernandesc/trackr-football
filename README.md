# Trackr.Football - API for football analytics

[![Build Status](https://travis-ci.com/diogofernandesc/trackr-football.svg?token=x7VLopamuyuGkPY4StCA&branch=master)](https://travis-ci.com/diogofernandesc/trackr-football) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/3ecfcb2b0f1040b48fa69a13f81a34f3)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=diogofernandesc/trackr-football&amp;utm_campaign=Badge_Grade) [![Codacy Badge](https://api.codacy.com/project/badge/Coverage/3ecfcb2b0f1040b48fa69a13f81a34f3)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=diogofernandesc/trackr-football&amp;utm_campaign=Badge_Coverage)

### API usage examples
Get teams with fantasy overall home strength greather than 100:
```
https://api.trackr.football/v1/team?fantasy_overall_home_strength=$gt:100
```

Get standings for teams with more than 10 points:
```
https://api.trackr.football/v1/standings?points=$gt:10
```

Get matches where the home team scored 3 goals
```
https://api.trackr.football/v1/match?full_time_home_score=3
```

Get data for Harry Kane
```
https://api.trackr.football/v1/player?name=Kane
```

## Contributing
Feel free to open a pull request, or open an issue to be investigated

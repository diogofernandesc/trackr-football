import React from 'react'
import { Bar, Line } from 'react-chartjs-2';
import {
    Badge,
    Button,
    ButtonDropdown,
    ButtonGroup,
    ButtonToolbar,
    Card,
    CardBody,
    CardFooter,
    CardHeader,
    CardTitle,
    Col,
    Dropdown,
    DropdownItem,
    DropdownMenu,
    DropdownToggle,
    Progress,
    Row,
    Table,
  } from 'reactstrap';
import { CustomTooltips } from '@coreui/coreui-plugin-chartjs-custom-tooltips';
import { getStyle, hexToRgba } from '@coreui/coreui/dist/js/coreui-utilities'
const brandInfo = getStyle('--info')
const brandPrimary = getStyle('--primary')
const brandSuccess = getStyle('--success')
const brandWarning = getStyle('--warning')
const brandDanger = getStyle('--danger')


// Card Chart 1
const cardChartData1 = {
  labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
  datasets: [
    {
      label: 'My First dataset',
      backgroundColor: brandPrimary,
      borderColor: 'rgba(255,255,255,.55)',
      data: [65, 59, 84, 84, 51, 55, 40],
    },
  ],
};

const cardChartOpts1 = {
  tooltips: {
    enabled: false,
    custom: CustomTooltips
  },
  maintainAspectRatio: false,
  legend: {
    display: false,
  },
  scales: {
    xAxes: [
      {
        gridLines: {
          color: 'transparent',
          zeroLineColor: 'transparent',
        },
        ticks: {
          fontSize: 2,
          fontColor: 'transparent',
        },

      }],
    yAxes: [
      {
        display: false,
        ticks: {
          display: false,
          min: Math.min.apply(Math, cardChartData1.datasets[0].data) - 5,
          max: Math.max.apply(Math, cardChartData1.datasets[0].data) + 5,
        },
      }],
  },
  elements: {
    line: {
      borderWidth: 1,
    },
    point: {
      radius: 4,
      hitRadius: 10,
      hoverRadius: 4,
    },
  }
}





// Card Chart 2
const cardChartData2 = {
    labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
    datasets: [
      {
        label: 'My First dataset',
        backgroundColor: brandInfo,
        borderColor: 'rgba(255,255,255,.55)',
        data: [1, 18, 9, 17, 34, 22, 11],
      },
    ],
  };
  
  const cardChartOpts2 = {
    tooltips: {
      enabled: false,
      custom: CustomTooltips
    },
    maintainAspectRatio: false,
    legend: {
      display: false,
    },
    scales: {
      xAxes: [
        {
          gridLines: {
            color: 'transparent',
            zeroLineColor: 'transparent',
          },
          ticks: {
            fontSize: 2,
            fontColor: 'transparent',
          },
  
        }],
      yAxes: [
        {
          display: false,
          ticks: {
            display: false,
            min: Math.min.apply(Math, cardChartData2.datasets[0].data) - 5,
            max: Math.max.apply(Math, cardChartData2.datasets[0].data) + 5,
          },
        }],
    },
    elements: {
      line: {
        tension: 0.00001,
        borderWidth: 1,
      },
      point: {
        radius: 4,
        hitRadius: 10,
        hoverRadius: 4,
      },
    },
  };


// Player Component
class Player extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: {}
    };
  }

  // Player selection count chart data
  
  buildSelectionData() {
    var gameWeeks = []
    var gameWeekSelection = []
    var i;
    for (i =1; i <= this.props.player_data.week_stats.length; i++) {
      gameWeeks.push("Gameweek " + i);
      gameWeekSelection.push(this.props.player_data.week_stats[i-1].fantasy_selection_count);
    }
    return [gameWeeks, gameWeekSelection];
  }

  getSelectionData() {
    var selecData = this.buildSelectionData();
    var cardChartSelecData = {
      labels: selecData[0],
      datasets: [
        {
          label: 'Fantasy selection count',
          backgroundColor: 'rgba(255,255,255,.3)',
          // backgroundColor: brandPrimary,
          borderColor: 'transparent',
          
          // borderColor: 'rgba(255,255,255,.55)',
          data: selecData[1],
        },
      ],
    }

    var cardChartSelecOpts1 = {
      // tooltips: {
      //   enabled: false,
      //   custom: CustomTooltips
      // },
      // maintainAspectRatio: false,
      // legend: {
      //   display: false,
      // },
      // scales: {
      //   xAxes: [
      //     {
      //       gridLines: {
      //         color: 'transparent',
      //         zeroLineColor: 'transparent',
      //       },
      //       ticks: {
      //         fontSize: 2,
      //         fontColor: 'transparent',
      //       },
    
      //     }],
      //   yAxes: [
      //     {
      //       display: false,
      //       ticks: {
      //         display: false,
      //         min: Math.min.apply(Math, cardChartSelecData.datasets[0].data) - 5,
      //         max: Math.max.apply(Math, cardChartSelecData.datasets[0].data) + 5,
      //       },
      //     }],
      // },
      // elements: {
      //   line: {
      //     borderWidth: 1,
      //   },
      //   point: {
      //     radius: 4,
      //     hitRadius: 10,
      //     hoverRadius: 4,
      //   },
      // }
      tooltips: {
        enabled: false,
        custom: CustomTooltips
      },
      maintainAspectRatio: false,
      legend: {
        display: false,
      },
      scales: {
        xAxes: [
          {
            display: false,
            barPercentage: 0.6,
          }],
        yAxes: [
          {
            display: false,
          }],
      },

    }
    console.log(cardChartSelecData);
    return [cardChartSelecData, cardChartSelecOpts1];
  }

  componentDidUpdate() {
    if (typeof this.props.player_data.week_stats !== 'undefined') {
      // var selectData = this.buildSelectionData();
    }
  }


  

  cardChartOpts1 = {
  tooltips: {
    enabled: false,
    custom: CustomTooltips
  },
  maintainAspectRatio: false,
  legend: {
    display: false,
  },
  scales: {
    xAxes: [
      {
        gridLines: {
          color: 'transparent',
          zeroLineColor: 'transparent',
        },
        ticks: {
          fontSize: 2,
          fontColor: 'transparent',
        },

      }],
    yAxes: [
      {
        display: false,
        ticks: {
          display: false,
          min: Math.min.apply(Math, cardChartData1.datasets[0].data) - 5,
          max: Math.max.apply(Math, cardChartData1.datasets[0].data) + 5,
        },
      }],
  },
  elements: {
    line: {
      borderWidth: 1,
    },
    point: {
      radius: 4,
      hitRadius: 10,
      hoverRadius: 4,
    },
  }
  }

  

  render() {
    return (
      <React.Fragment>
        <Col xs="12" sm="6" lg="3">
            <Card className="text-white ">
                <CardBody >
                {/* https://resources.premierleague.com/premierleague/photos/players/250x250/p78830.png */}
                    <img src={`https://resources.premierleague.com/premierleague/photos/players/250x250/p${this.props.player_data.photo_url}`} width='100%' height='auto' alt="admin@bootstrapmaster.com" />
                </CardBody>
            </Card> 
        </Col>
      
        <Col xs="24" sm="12" lg="3">
            <Card className="text-black ">
                <CardBody className="pb-0">
                    <div className="progress-group">
                        <div className="progress-group-header">
                        {/* <i className="icon-user progress-group-icon"></i> */}
                        <span className="title">Name</span>
                        <span className="ml-auto font-weight-bold">{this.props.player_data.name}</span>
                        </div>
                        <div className="progress-group-bars">
                        <Progress className="progress-xs" color="warning" value="0" />
                        </div>
                    </div>
                    <div className="progress-group">
                        <div className="progress-group-header">
                        {/* <i className="icon-user progress-group-icon"></i> */}
                        <span className="title">Club</span>
                        <span className="ml-auto font-weight-bold">{this.props.player_data.team}</span>
                        </div>
                        <div className="progress-group-bars">
                        <Progress className="progress-xs" color="warning" value="0" />
                        </div>
                    </div>
                    <div className="progress-group">
                        <div className="progress-group-header">
                        {/* <i className="icon-user progress-group-icon"></i> */}
                        <span className="title">Nationality</span>
                        <span className="ml-auto font-weight-bold">{this.props.player_data.nationality}</span>
                        </div>
                        <div className="progress-group-bars">
                        <Progress className="progress-xs" color="warning" value="0" />
                        </div>
                    </div>
                    <div className="progress-group">
                        <div className="progress-group-header">
                        {/* <i className="icon-user progress-group-icon"></i> */}
                        <span className="title">Position</span>
                        <span className="ml-auto font-weight-bold">{this.props.player_data.position}</span>
                        </div>
                        <div className="progress-group-bars">
                        <Progress className="progress-xs" color="warning" value="0" />
                        </div>
                    </div>
                    <div className="progress-group">
                        <div className="progress-group-header">
                        {/* <i className="icon-user progress-group-icon"></i> */}
                        <span className="title">Fantasy price</span>
                        <span className="ml-auto font-weight-bold">{this.props.player_data.fantasy_price}</span>
                        </div>
                        <div className="progress-group-bars">
                        <Progress className="progress-xs" color="warning" value="0" />
                        </div>
                    </div>
                    <div className="progress-group">
                        <div className="progress-group-header">
                        {/* <i className="icon-user progress-group-icon"></i> */}
                        <span className="title">Fantasy selection %</span>
                        <span className="ml-auto font-weight-bold">{this.props.player_data.fantasy_selection_percentage}</span>
                        </div>
                    </div>
                </CardBody>
            </Card>
        </Col>
        <Col xs="12" sm="6" lg="3">
        <Card className="text-white bg-success">
              <CardBody className="pb-0">
                <ButtonGroup className="float-right">
                  <ButtonDropdown id='card4' isOpen={this.state.card4} toggle={() => { this.setState({ card4: !this.state.card4 }); }}>
                    <DropdownToggle caret className="p-0" color="transparent">
                      <i className="icon-settings"></i>
                    </DropdownToggle>
                    <DropdownMenu right>
                      <DropdownItem>Action</DropdownItem>
                      <DropdownItem>Another action</DropdownItem>
                      <DropdownItem>Something else here</DropdownItem>
                    </DropdownMenu>
                  </ButtonDropdown>
                </ButtonGroup>
                <div className="text-value">{this.props.player_data.week_stats[this.props.player_data.week_stats.length-1].fantasy_selection_count}</div>
                <div>Fantasy Selection Count</div>
              </CardBody>
              <div className="chart-wrapper mx-3" style={{ height: '70px' }}>
                <Bar data={this.getSelectionData()[0]} options={this.getSelectionData()[1]} height={70} />
              </div>
            </Card>
          </Col>
      </React.Fragment>
  )
  }


}




export default Player
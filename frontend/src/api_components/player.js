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


const Player = ({ player }) => {
    return (
        <React.Fragment>
        <Col xs="12" sm="6" lg="3">
            <Card className="text-white ">
                <CardBody >
                {/* https://resources.premierleague.com/premierleague/photos/players/250x250/p78830.png */}
                    <img src={`https://resources.premierleague.com/premierleague/photos/players/250x250/p${player.photo_url}`} width='100%' height='auto' alt="admin@bootstrapmaster.com" />
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
                        <span className="ml-auto font-weight-bold">{player.name}</span>
                        </div>
                        <div className="progress-group-bars">
                        <Progress className="progress-xs" color="warning" value="0" />
                        </div>
                    </div>
                    <div className="progress-group">
                        <div className="progress-group-header">
                        {/* <i className="icon-user progress-group-icon"></i> */}
                        <span className="title">Club</span>
                        <span className="ml-auto font-weight-bold">{player.team}</span>
                        </div>
                        <div className="progress-group-bars">
                        <Progress className="progress-xs" color="warning" value="0" />
                        </div>
                    </div>
                    <div className="progress-group">
                        <div className="progress-group-header">
                        {/* <i className="icon-user progress-group-icon"></i> */}
                        <span className="title">Nationality</span>
                        <span className="ml-auto font-weight-bold">{player.nationality}</span>
                        </div>
                        <div className="progress-group-bars">
                        <Progress className="progress-xs" color="warning" value="0" />
                        </div>
                    </div>
                    <div className="progress-group">
                        <div className="progress-group-header">
                        {/* <i className="icon-user progress-group-icon"></i> */}
                        <span className="title">Position</span>
                        <span className="ml-auto font-weight-bold">{player.position}</span>
                        </div>
                        <div className="progress-group-bars">
                        <Progress className="progress-xs" color="warning" value="0" />
                        </div>
                    </div>
                    <div className="progress-group">
                        <div className="progress-group-header">
                        {/* <i className="icon-user progress-group-icon"></i> */}
                        <span className="title">Fantasy price</span>
                        <span className="ml-auto font-weight-bold">{player.fantasy_price}</span>
                        </div>
                        <div className="progress-group-bars">
                        <Progress className="progress-xs" color="warning" value="0" />
                        </div>
                    </div>
                    <div className="progress-group">
                        <div className="progress-group-header">
                        {/* <i className="icon-user progress-group-icon"></i> */}
                        <span className="title">Fantasy selection %</span>
                        <span className="ml-auto font-weight-bold">{player.fantasy_selection_percentage}</span>
                        </div>
                    </div>
                </CardBody>
            </Card>
        </Col>
        </React.Fragment>
    )
}

export default Player
import React, { Component } from 'react';
import { render } from "react-dom";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend} from "recharts";
import { sortBy } from "lodash";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      loaded: false,
      placeholder: "Loading"
    };
  }

  componentDidMount() {
    fetch("ksfront")
      .then(response => {
        if (response.status > 400) {
          return this.setState(() => {
            return { placeholder: "Something went wrong!" };
          });
        }
        return response.json();
      })
      .then(data => {
        this.setState(() => {
          return {
            data,
            loaded: true
          };
        });
      });
  }

  render() {
    // console.log(this.state.data);
    var chart_data = this.state.data;
    chart_data = _.sortBy(chart_data, ['delivery_time', 'usd_price']);
    // console.log(chart_data);
    var new_chart_data = [chart_data[0]];
    console.log(new_chart_data);
    var index, len;
    var new_index = 0;

    for (index = 1, len = chart_data.length; index < len; ++index) {
        if (chart_data[index]['delivery_time'] == chart_data[index - 1]['delivery_time']) {
            new_chart_data[new_index]['usd_price'] = new_chart_data[new_index]['usd_price'] + chart_data[index]['usd_price'];
        } else {
            new_index += 1;
            new_chart_data.push(chart_data[index]);
        }
    }
    console.log(new_chart_data);

    var total_price = 0;
    var price;
    for (var val in chart_data) {
        total_price += chart_data[val]['usd_price'];
    }
    console.log(total_price);
    chart_data = _.sortBy(chart_data, ['id', 'usd_price']);

    // this.state.data.forEach(function(){
    //     chart_data += {}
    // })
    return (
        <div className="App">
            <div class="chart">
                <LineChart width={800} height={400} data={new_chart_data}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <XAxis dataKey="delivery_time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="usd_price" stroke="#000" />
                </LineChart>
            </div>
            <div class="total_price">
                <div class="total_text">Total</div>
                <div class="total_sum">{total_price}</div>
            </div>
            <div class="info_table">
                <table>
                    <thead>
                        <tr>
                            <td>№</td>
                            <td>Заказ №</td>
                            <td>Стоимость $</td>
                            <td>Срок поставки</td>
                        </tr>
                    </thead>
                    <tbody>
                    {chart_data.map(db_data => {
                        return(
                            <tr>
                            <td>{db_data.id}</td>
                            <td>{db_data.order_no}</td>
                            <td>{db_data.usd_price}</td>
                            <td>{db_data.delivery_time}</td>
                        </tr>
                        )
                    })}
                    </tbody>
                </table>
            </div>
        </div>
        
      );
    // return (
    //   <ul>
        // {this.state.data.map(db_data => {
        //   return (
        //     <li key={db_data.id}>
        //       {db_data.order_no} - {db_data.usd_price} - {db_data.delivery_time}
        //     </li>
        //   );
        // })}
    //   </ul>
    // );
  }
}

export default App;

const container = document.getElementById("app");
render(<App />, container);
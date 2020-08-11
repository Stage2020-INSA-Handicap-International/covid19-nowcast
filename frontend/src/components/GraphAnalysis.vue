<template>
  <div>
    <!-- Graph Analysis Header -->
    <div class="container-1">
      <div class="title-1">Graphical Analysis</div>        
    </div>
    <!-- Graph Analysis Body -->
    <div class="container-2">
      <div class="graph-chart"><canvas id="graphChart" width="1000" height="800"></canvas></div>
      <div class="container-3 graph-parameters">
        <div class="container-4 ">
            <div class="title-2">Topics</div>
            <div class = "combobox"><input id="selected-topic-for-graph" type="number" value="0" min="0" :max='nb_topics - 1' /></div>
            <div> All <input id="all-checkbox" type="checkbox"/></div>
        </div>
        <div class="container-5 ">
            <div class="title-2">Timeframe</div>
            <select class="combobox-2" id="selected-timeframe" v-on:change="changeTimeFrame()">
              <option v-for="timeframe in timeframes" v-bind:key="timeframe.id">{{timeframe}}</option>
            </select>
        </div>        
        <div><button v-on:click="sendGraphRequest()">FILTER</button></div>   
    </div>
    </div>
  </div>
</template>

<script>
  import $ from 'jquery'
  import {eventBus} from "../main.js"
  import Chart from 'chart.js'
  import moment from 'moment';

  export default {
    name: 'GraphAnalysis',
    data: function() {
      return {
        nb_topics: 3,
        selected_topic:'0',
        all_checkbox:false,
        timeframes:['Weekly','Daily','Monthly'],
        myChart: [],
        data:[],
        arrayColumn : (arr, n) => arr.map(x => x[n]),
        default_data: [],
        default_labels: [],
        default_type :'line',
        default_unit: 'week',
        default_title:'',
        colors: ['red', 'blue', 'limegreen'],
        tags: ['negative', 'neutral', 'positive']
         
      }
    },

    methods : {
      sendGraphRequest: function () {
        //Save the parameters
        var input_nb_topic = document.getElementById("selected-topic-for-graph").value;
        this.selected_topic = parseInt(input_nb_topic,10);
        this.all_checkbox =  document.getElementById("all-checkbox").checked
        //Prepare the json object that will serve as the HTTP POST Request's body
        var request_body = JSON.stringify(
        {
          "topic":{"all":this.all_checkbox,"topic_id":this.selected_topic}
        })
        //Launch the HTTP POST Request to the server
        var vm = this;
        $.post( "http://127.0.0.1:8000/graph/", request_body)
            .done( function(data) {
              //alert( "[TopicAnalysis] Data Loaded: " + data );
              data = JSON.parse(data);
              vm.draw_graph(data);
              

            });     
      },

      changeTimeFrame: function() {
        var timeframe = document.getElementById("selected-timeframe").value;
        var converter = {'Weekly':'week','Daily':'day','Monthly':'month'};
        this.default_unit = converter[timeframe]
        console.log('default_unit = '+this.default_unit)
        this.sendGraphRequest();
      },    

      draw_graph: function(response) {
        var data = response['data']
        var analysis = []
        var dates = []
        var len = this.tags.length
        var tag_count = new Array(len).fill(0)

        if (this.default_unit == 'week') {
          var transform = (date) => moment(date).week()
          var reverse = (number) => moment('2020').add(number, 'weeks')
        } 
        else if (this.default_unit == 'month'){
          transform = (date) => moment(date).month()
          reverse = (number) => moment('2020').add(number, 'month')
       } 
       else { 
          transform = (date) => date
          reverse = (number) => number
       }

      dates.push(transform(new Date(data[0].created_at).toDateString("yyyy-MM-dd")))
      for (i in data) {
        if (dates.indexOf(transform(new Date(data[i].created_at).toDateString("yyyy-MM-dd"))) == -1){
          analysis.push(tag_count)
          dates.push(transform(new Date(data[i].created_at).toDateString("yyyy-MM-dd")))
          tag_count = new Array(len).fill(0)
        }
        tag_count[this.tags.indexOf(data[i].sentiment)]++
      }
      console.log(dates)
      analysis.push(tag_count)
      dates = dates.map(date => new Date(reverse(date)))

        this.default_labels = dates
        this.default_data = analysis
        var tagged_dataset = [];
        for (var i = 0; i < len; i++) {
          tagged_dataset.push({
                label: this.tags[i],
                data: this.arrayColumn(this.default_data,i),
                borderColor: this.colors[i],
                borderWidth: 1
            });
        }
      if(dates.length == 1){
            this.default_type = 'bar'
      }

      // if the chart is not undefined (e.g. it has been created)
      // then destory the old one so we can create a new one later
      if (this.myChart && this.myChart instanceof Chart) {
        this.myChart.destroy();
        console.log("destroyed myChart")
      }

      var ctx = document.getElementById('graphChart').getContext('2d');
      this.myChart = new Chart(ctx, {
          type: this.default_type,
          label: 'Sentiment',
          data: {
              labels: this.default_labels,
              datasets: tagged_dataset
          },
          options: {
              scales: {
                  xAxes: [{
                      type: 'time',
                      time: {
                          unit: this.default_unit
                      }
                  }]
              },
              legend: {
                position: 'right'
              },
              title: {
                  display: true,
                  text: this.default_title
              }
          }
      });
      console.log(this.myChart);
      }      
    },

    created() {
      eventBus.$on('nbTopicsChange', (new_nb_topics) => {
        //console.log('[GraphAnalysis] received nbTopicsChange event');
        this.nb_topics = new_nb_topics;
      });
    },


  }

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

  .container-1 {
    display:flex;
    background-color: #5D9DC1;
    padding:20px;
  }

  .container-2 {
    display:flex;
    /*background-color: red;*/
    
  }  

  .container-3 {
    display:flex;
    flex-direction: column;
    align-items:center;
    flex-grow:1;
    /*background-color: yellow;*/
  }   
  .container-4 {
    display:flex;
  }   
  .container-5 {
    display:flex;
  }   
  
  .graph-chart {
    /*background-color: green;*/
  }   
  .title-1 {
    color:white;
    font-size:20px;
    padding-right:60px;
  }
  .title-2 {
    color:#4786A9;
    font-size:25px;
    font-weight:bold;
    padding-right:20px;
    padding-bottom:40px;
    margin-right:20px;
  }

  .graph-parameters {
    background-color: #E7EEF2;
    padding:20px;
  }

  input[type="number"], textarea {
    background-color : white; 
    text-align: center;
  }

  .combobox {
    padding-right:20px;
  }

  .combobox select, input {
    width:40px;
    height:30px;
    background-color:#EEEEEE;
    border: transparent;
    border-radius:6px;
  } 

  .combobox-2 {
    width:100px;
    height:30px;
    background-color:white;
    border: transparent;
    border-radius:6px;
    padding-left:20px;
  }

  button {
    width:150px;
    height:80px;
    background-color:#FFFFFF;
    font-weight:bold;
    font-size:20px;
    color:#5D9DC1;
    border: transparent;
    border-radius:6px;
  }





</style>

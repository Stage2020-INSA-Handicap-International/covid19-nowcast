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
        <div><button v-on:click="sendGraphRequest()">LAUNCH</button></div>   
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
        default_cases: [],
        default_type :'line',
        default_unit: 'week',
        default_title:'',
        default_rolling_option: 'Confirmed',
        colors: ['red', 'blue', 'limegreen', 'black', 'orange', 'indigo'],
        tags: ['negative', 'neutral', 'positive', 'confirmed cases', 'deaths', 'recovered']
      }
    },

    methods : {

      sortByDate: function(a, b) {
          return new Date(a[0].created_at) - new Date(b[0].created_at);
      },

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
        $.post( "http://0.0.0.0:8000/graph/", request_body)
            .done( function(data) {
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
      
      compare_dates: function(date1,date2){
        if (date1<date2) return true
        else return false
      },

      draw_graph: function(response) {
        var data = response['data']
        var cases = response['cases']
        var rolling_cases_dataset = []

        data = Object.values(data).sort((a, b) => new Date(a.created_at)>new Date(b.created_at)); // Sort date in data (ascending)


        /**  Init variables
         * Our variables are seperated in two categories : counters and arrays per timeframe
         * tag_count counts the number of labels tweets per timeframe : tag_count[0] -> neg, [1] -> neut, [2] -> pos
         * case_count counts the cases per timeframe : case_count[0] -> Confirmed, [1] -> Deaths, [2] -> Recovered
         * analysis, num_cases and all_tweets are arrays of all the data concatenated
         * dates is an array of all the dates found in data and cases (it is dynamically generated)
         */
        var analysis = []
        var num_cases = []
        var all_tweets = new Array(cases.length).fill(0)
        var dates = []
        var len = 3
        var tag_count = new Array(len).fill(null)
        var case_count = new Array(len).fill(0)

        /** Transformation from days to desired timeframe
         * In order to filter the information to our current timeframe, we first convert our day to the desired timeframe (week or month)
         * and then reverse the transformation in order to get the start of week or month.
         */
        if (this.default_unit == 'week') {
          var transform = (date) => moment(date).isoWeek()-1
          var reverse = (number) => moment('2020').day("Monday").add(number, 'weeks')
        } 
        else if (this.default_unit == 'month'){
          transform = (date) => moment(date).month()
          reverse = (number) => moment('2020').add(number, 'month')
        } 
        else { 
          transform = (date) => date
          reverse = (number) => number

        /** Calculate rolling average
         * Rolling Average is only calculated if selected timeframe is day.
         */
        var rolling_cases = []
        if (this.default_rolling_option == 'Confirmed') 
        { 
          var role_option = (o) => o.Confirmed
        }
        else role_option = (o) => o.Deaths
        rolling_cases.push(role_option(cases[0]))
        for (var m = 1; m < cases.length-1; m++)
          {
              var mean = (role_option(cases[m]) + role_option(cases[m-1]) + role_option(cases[m+1]))/3.0;
              rolling_cases.push(mean);
          }
        rolling_cases.push(role_option(cases[cases.length-1]))
        rolling_cases_dataset = [{
          label: this.default_rolling_option+' Case (± 3days)',
              data: rolling_cases,
              borderColor: 'darkgrey',
              borderWidth: 1,
              yAxisID: 'cases_count',
              hidden: true,
              fill: false
        }]
      }

      /// Processing data for the graph ///
      /** Init variables
       * tweet is the current tweet counter
       * cur_date is the date in the first none processed data
       * idx is the index of the curr_date in dates (it allows us to know if we have already seen this date or not)
       */
      var tweet=0
      var cur_date = new Date(data[tweet].created_at).toDateString("yyyy-MM-dd")
      var idx = dates.indexOf(transform(cur_date))

      /** Check if we have data before our first case
       * continu is a variable that checks if we have tweets prior to the first case
       * if we do, we add the curr_date to our dates and process the data
       */
      var continu = this.compare_dates(new Date(cur_date), new Date((new Date(cases[0].Date).toDateString("yyyy-MM-dd"))))
      if(continu) dates.push(transform(cur_date))
      while(continu && tweet < data.length) {
        idx = dates.indexOf(transform(cur_date))
        if (idx == -1){ //curr_date was not already found (not in dates)
          // add vars to our arrays and init var
          analysis.push(tag_count)
          num_cases.push([0, 0, 0])
          dates.push(transform(cur_date))
          tag_count = new Array(len).fill(0)
        }
        // process data
        tag_count[this.tags.indexOf(data[tweet].sentiment)]++
        tweet++
        cur_date = new Date(data[tweet].created_at).toDateString("yyyy-MM-dd")
        continu = this.compare_dates(new Date(cur_date), new Date((new Date(cases[0].Date).toDateString("yyyy-MM-dd"))))
      }
      analysis.push(tag_count)

      /** Processing data within cases
       * 1. Check if cases[j] timeframe has already been found (is in dates)
       * 2a. If not, add it to dates
       * 3a. While data[tweet] timeframe is found : process data
       * 2b. Else add vars to our arrays and init var
       */
      for (var j=0; j<cases.length; j++){
        if (dates.indexOf(transform(new Date(cases[j].Date).toDateString("yyyy-MM-dd"))) == -1){
          if(j>0) num_cases.push(case_count)
          dates.push(transform(new Date(cases[j].Date).toDateString("yyyy-MM-dd")))
          case_count = new Array(len).fill(0)
          idx = dates.indexOf(transform(cur_date))
          while (idx != -1 && tweet < data.length){
            tag_count[this.tags.indexOf(data[tweet].sentiment)]++
            tweet=tweet+1
            if (tweet < data.length){
              cur_date = new Date(data[tweet].created_at).toDateString("yyyy-MM-dd")
              idx = dates.indexOf(transform(cur_date))
            } else idx = -1
          }
          if(j<cases.length-1) analysis.push(tag_count)
        }
        case_count[0]=cases[j].Confirmed
        case_count[1]=cases[j].Deaths
        case_count[2]=cases[j].Recovered
        if(j<cases.length-1) tag_count = new Array(len).fill(0)
      }
      num_cases.push(case_count)

      /** Check if we have data after our last case
       * if we do, we add the curr_date to our dates and process the data
       */
      while (tweet < data.length){
        idx = dates.indexOf(transform(cur_date))
        if (idx == -1){
          analysis.push(tag_count)
          num_cases.push([null, null, null])
          cur_date = new Date(data[tweet].created_at).toDateString("yyyy-MM-dd")
          idx = dates.indexOf(transform(cur_date))
          dates.push(transform(cur_date))
          tag_count = new Array(len).fill(0)
        }
        tag_count[this.tags.indexOf(data[tweet].sentiment)]++
        tweet++
      }
      analysis.push(tag_count)

      // Convert the dates to start of week, day or month
      dates = dates.map(date => new Date(reverse(date)))

      // Create our all_tweets array
      for(var a in analysis){
        all_tweets[a] = analysis[a][0] + analysis[a][1] + analysis[a][2]
      }

      // Find the first labeled twwet
      var index1 = all_tweets.findIndex(function(number) {
        return number > 0;
      });
      // Set the first date of our graph as the date of the first labeled tweet
      var date1 = dates[index1-1]

      /// Generating Graph ///
      this.default_labels = dates
      this.default_data = analysis
      this.default_cases = num_cases

      // Sentiment dataset used for chart
      var tagged_dataset = [];
      for (var i = 0; i < len; i++) {
        tagged_dataset.push({
              label: this.tags[i],
              data: this.arrayColumn(this.default_data,i),
              borderColor: this.colors[i],
              borderWidth: 1,
              yAxisID: 'sentiment_count',
              fill: false
          });
        }
        // Cases dataset used for chart
        var cases_dataset = [];
        for (var k = 3; k < len+3; k++) {
          cases_dataset.push({
                label: this.tags[k],
                data: this.arrayColumn(this.default_cases,k-3),
                borderColor: this.colors[k],
                borderWidth: 1,
                yAxisID: 'cases_count',
                fill: false
            });
        }
        // All tweets dataset used for chart
        var all_tweets_dataset = [{
                label: 'tweet count',
                data: all_tweets,
                borderColor: 'grey',
                borderWidth: 1,
                yAxisID: 'sentiment_count',
                hidden: true,
                fill: false
            }];
      if(dates.length == 1){
            this.default_type = 'line'
      } else this.default_type = 'line'

      // if the chart is not undefined (e.g. it has been created)
      // then destory the old one so we can create a new one later
      if (this.myChart && this.myChart instanceof Chart) {
        this.myChart.destroy();
      }
      // Creating chart
      var ctx = document.getElementById('graphChart').getContext('2d');
      this.myChart = new Chart(ctx, {
          type: this.default_type,
          label: 'Sentiment',
          data: {
              labels: this.default_labels,
              datasets: tagged_dataset.concat(all_tweets_dataset).concat(cases_dataset).concat(rolling_cases_dataset)
          },
          options: {
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        unit: this.default_unit
                    },
                    ticks: {
                        min: date1 // Used to remove everything before a certain date
                    }
                }],
                yAxes: [{
                    id: 'sentiment_count',
                    type: 'linear',
                    position: 'left',
                }, {
                    id: 'cases_count',
                    type: 'linear',
                    position: 'right',
                }]
            },
            legend: {
              position: 'right'
            },
            title: {
                display: true,
                text: this.default_title
            },
          }
      });
      }      
    },

    created() {
      eventBus.$on('nbTopicsChange', (new_nb_topics) => {
        this.nb_topics = new_nb_topics;
      });
      eventBus.$on('launchGraphAnalysis', () => {
        this.sendGraphRequest();
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

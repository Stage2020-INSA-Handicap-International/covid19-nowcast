<template>
  <div>
    <!-- Graph Analysis Header -->
    <div class="container-1">
      <div class="title-1">Graphical Analysis</div>        
    </div>
    <!-- Graph Analysis Body -->
    <div class="container-2">
      <div class="graph-chart"><canvas id="graphChart"></canvas></div>
      <div class="container-3 graph-parameters">
        <div class="container-4 ">
            <div class="title-2">Topics</div>
            <div class = "combobox"><input id="selected-topic-for-graph" type="number" value="0" min="0" :max='nb_topics - 1' /></div>
            <div> All <input id="all-checkbox" type="checkbox"/></div>
        </div>
        <div><button v-on:click="sendGraphRequest()">FILTER</button></div>   
    </div>
    </div>
  </div>
</template>

<script>
  //import $ from 'jquery'
  import {eventBus} from "../main.js"
  import Chart from 'chart.js'
  import moment from 'moment';

  export default {
    name: 'GraphAnalysis',
    data: function() {
      return {
        nb_topics: 3,
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

    methods : {},

    created() {
      eventBus.$on('nbTopicsChange', (new_nb_topics) => {
        //console.log('[GraphAnalysis] received nbTopicsChange event');
        this.nb_topics = new_nb_topics;
      });
    },

    sendTopicListRequest: function () {
      //Save the parameters
      var input_nb_topics = document.getElementById("selected-nb-topics").value;
      this.nb_topics = parseInt(input_nb_topics,10);
      //Prepare the json object that will serve as the HTTP POST Request's body
      var request_body = JSON.stringify(
      {
        "nb_topics":this.nb_topics
      })
      //Launch the HTTP POST Request to the server
      var vm = this;
      $.post( "http://127.0.0.1:8000/topics/", request_body)
          .done( function(data) {
            //alert( "[TopicAnalysis] Data Loaded: " + data );
            data = JSON.parse(data);
            vm.topics = data["topics"];
            for(var i =0; i<vm.topics.length; i++) {
              vm.topics[i] = vm.topics[i].join(', ');
            }
            //If there are no topics it means there are no tweets, therefore there's no need to try to get examples
            if(vm.topics.length !== 0) {
              eventBus.$emit('getTopicExamples');
            }
            else {
              //Clear examples view
              vm.examples = [];

              //Clear n_grams view

              $('#canvas').html('');
              var canvas = document.getElementById("canvas");
              var context = canvas.getContext("2d");
              // Store the current transformation matrix
              context.save();
              // Use the identity matrix while clearing the canvas
              context.setTransform(1, 0, 0, 1, 0, 0);
              context.clearRect(0, 0, canvas.width, canvas.height);
              // Restore the transform
              context.restore();
              //ctx.clearRect(0,0,canvas.width,canvas.height);
            }
            

          });
    },    

    draw_graph: function(response) {
      var data = JSON.parse(response).request
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
    var ctx = document.getElementById('myChart').getContext('2d');
    var myChart = new Chart(ctx, {
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
    console.log(myChart);
    }
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
    flex-grow:1;
    /*background-color: red;*/
    
  }  

  .container-3 {
    display:flex;
    flex-direction: column;
    align-items:center;
    /*background-color: yellow;*/
  }   
  .container-4 {
    display:flex;
    /*background-color: blue;*/

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

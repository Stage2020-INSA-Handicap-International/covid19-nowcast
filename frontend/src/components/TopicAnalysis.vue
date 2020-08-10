<template>
  <div>
    <!-- Topic Analysis Header -->
    <div class="container-2">
      <div class="title-1">Topic Analysis</div>
      <div class="title-2">Number of Topics</div>
      <div class = "combobox"><input id="selected-nb-topics" type="number" value="3" min="1" v-on:change="notifyGraphAnalysis()"/></div>
      <button v-on:click="sendTopicListRequest()">APPLY</button>
      <!--<button v-on:click="get()">GET</button>-->          
    </div>
    <!-- Topic Analysis Body -->
    <div class="container-3">
      <div class="container-4">
        <div id="topic-list" class="topic-box">
          <p class="title-3"> Topic List </p>
          <li v-for="topic in topics" v-bind:key="topic.id">
            {{topic}}
          </li>
        </div>
        <div class="topic-box">
          <div class="title-4">N-GRAMS</div>
          <!--<img :src='"data:image/png;base64, "+n_grams_img' alt="n-gram diagram image">-->
          <canvas id="canvas" width=600></canvas>
        </div>
      </div>
      <div class="container-5 topic-box">
        <div class="container-6">
          <div class="title-4">Topic Examples</div>
          <div>Topic <input id="selected-topic-for-examples" type="number" value="0" min="0" :max='nb_topics - 1' /></div>
          <div> Number of Examples <input id="selected-nb-examples" type="number" value="3" min="1"/></div>
       </div>
       <div class="container-7">
        <div class = "scrollbar">
            <div class="tweet-example" v-for="example in examples" v-bind:key="example.id">{{example}}</div>
        </div>
       </div>
     </div>

    </div>
  </div>
</template>

<script>
  import $ from 'jquery'
  import {eventBus} from "../main.js"

  export default {
    name: 'TopicAnalysis',
    data: function() {
      return {
         nb_topics : 3,
        'selected_topic_for_examples':0,
        'selected_nb_examples':3,
         topics : [],
         examples: [],
         n_grams_img:[],
      }
    },
    watch: {
      // whenever topics change, this function will run
      topics: function (newTopics, oldTopics) {
        console.log('newTopics : '+ newTopics + '- oldTopics : '+oldTopics)
        console.log("TOPICS HAVE CHANGED")
        //this.answer = 'Waiting for you to stop typing...'
        //this.debouncedGetAnswer()
      }
    },

  methods : {
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
    sendTopicExamplesRequest: function() {
      //Save the parameters
      var input_topic_for_examples = document.getElementById("selected-topic-for-examples").value;
      this.selected_topic_for_examples = parseInt(input_topic_for_examples,10);
      var input_nb_examples = document.getElementById("selected-nb-examples").value;
      this.selected_nb_examples = parseInt(input_nb_examples,10);   
      
      //Prepare the json object that will serve as the HTTP POST Request's body
      var vm = this;
      var request_body = JSON.stringify(
      {
        "topic":this.selected_topic_for_examples,
        "nb_examples":this.selected_nb_examples
      }) 
      //Launch the HTTP POST Request to the server
      $.post( "http://127.0.0.1:8000/examples/", request_body)
          .done( function(data) {
            //alert( "[Examples] Data Loaded: " + data );
            data = JSON.parse(data);
            //Set examples
            vm.examples = data["examples"];
            vm.n_grams_img = data["graph"]
            vm.resize_img()
          }); 
    },
    get: function () {
      //Launch the HTTP POST Request to the server
      $.get( "http://127.0.0.1:8000/access/")
          .done(function( data ) {
            alert( "Data Loaded: " + JSON.stringify(data) );
          });      
    }, 
    resize_img: function() {
      var canvas = document.getElementById("canvas");
      var ctx = canvas.getContext("2d");
      var img = new Image();
      img.src = "data:image/png;base64, "+this.n_grams_img

      img.onload = function () {

          // set size proportional to image
          canvas.height = canvas.width * (img.height / img.width);

          ctx.drawImage(img, 0, 0, img.width,    img.height,     // source rectangle
                         0, 0, canvas.width, canvas.height);
      }

    },  
    notifyGraphAnalysis: function() {
      var input_nb_topics = document.getElementById("selected-nb-topics").value;
      this.nb_topics = parseInt(input_nb_topics,10);
      eventBus.$emit('nbTopicsChange',this.nb_topics);
    },

  },

  created() {
    eventBus.$on('launchTopicAnalysis', () => {
      this.sendTopicListRequest();
    });
    eventBus.$on('getTopicExamples', () => {
      this.sendTopicExamplesRequest();
    })
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

  input[type="number"], textarea {
    background-color : white; 
    text-align: center;
  }

  select, textarea {
    background-color : white; 
    text-align: center;
    padding:5px;
  }
  select {
    margin:5px;
    border-radius: 10px;
  }
  .container-2 {
    display:flex;
    background-color: #5D9DC1;
    padding:20px;
  }

  .container-3 {
    display:flex;
    
    
  }

  .container-4 {
    display:flex;
    flex-direction: column;
    
  }

  .container-5 {
    display:flex;
    flex-direction: column;
    flex-grow:1;

  }

  .container-6 {
    display:flex;
    
  }

  .container-7 {
    display:flex;
    flex-direction: column;
    
  }
  .scrollbar {
    max-height:1000px;
    overflow-y:auto;
  }

  .title-1 {
    color:white;
    font-size:20px;
    padding-right:60px;
  }

  .title-2 {
    color:white;
    font-size:18px;
    padding-right:20px;
  }

  .title-3 {
    color:#4786A9;
    font-size:25px;
    font-weight:bold;
    padding-right:20px;
    padding-bottom:40px;
    text-align:center;
  }

  .title-4 {
    color:#4786A9;
    font-size:25px;
    font-weight:bold;
    padding-right:20px;
    padding-bottom:40px;
    margin-right:20px;
  }

  .topic-box {
    background-color:#E7EEF2;
    padding:20px;
    margin:20px;
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

  .tweet-example {
    background-color:#C4C4C4;
    padding:20px;
    margin:20px;
    border-radius:10px;
  }



  button {
    width:100px;
    background-color:#FFFFFF;
    font-weight:bold;
    color:#5D9DC1;
    border: transparent;
    border-radius:6px;
  }





</style>

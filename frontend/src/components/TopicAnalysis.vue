<template>
  <div>
    <!-- Topic Analysis Header -->
    <div class="container-2">
      <div class="title-1">Topic Analysis</div>
      <div class="title-2">Topic Count</div>
      <div class = "combobox"><input id="selected-topic-count" type="number" value="3"/></div>
      <button v-on:click="sendRequest()">APPLY</button>
      <button v-on:click="get()">GET</button>          
    </div>
    <!-- Topic Analysis Body -->
    <div class="container-3">
      <div class="container-4">
        <div class="topic-box">coucou</div>
        <div class="topic-box">coucou</div>
      </div>
        <div class="topic-box">coucou</div>
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
        'topic_count' : 3
      }
    },

  methods : {
    sendRequest: function () {
      //Save the parameters
      var input_value = document.getElementById("selected-topic-count").value;
      this.topic_count = parseInt(input_value,10);
      alert(this.topic_count);
      //Prepare the json object that will serve as the HTTP POST Request's body
      var request_body = JSON.stringify(
      {
        "nb_topics":this.topic_count
      })
      //Launch the HTTP POST Request to the server
      $.post( "http://127.0.0.1:8000/topics/", request_body)
          .done(function( data ) {
            alert( "[TopicAnalysis] Data Loaded: " + JSON.stringify(data) );
          });      
    },
    get: function () {
      //Launch the HTTP POST Request to the server
      $.get( "http://127.0.0.1:8000/access/")
          .done(function( data ) {
            alert( "Data Loaded: " + JSON.stringify(data) );
          });      
    },    
  },

  created() {
    eventBus.$on('launchTopicAnalysis', () => {
      alert('coucou depuis topicAnalysis');
      this.sendRequest();
    })
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .container-2 {
    display:flex;
    background-color: #5D9DC1;
    padding:20px;
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
    width:100px;
    background-color:#FFFFFF;
    font-weight:bold;
    color:#5D9DC1;
    border: transparent;
    border-radius:6px;
  }

  .container-3 {
    display:flex;
    
  }

  .container-4 {
    display:flex;
    flex-direction: column;
  }

  .topic-box {
    background-color:#E7EEF2;
    padding:20px;
    margin:20px;
  }



</style>

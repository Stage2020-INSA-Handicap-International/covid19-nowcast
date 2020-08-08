<template>
  <div class="container-2">

    <div class="title">Country</div>
    <div class = "combobox">
      <select id="selected-country">
        <option>-- Select a Country --</option>
        <option v-for="country in countries" v-bind:key="country.id">{{country}}</option>
      </select>
    </div>

    <div class="title">Source</div>
    <div class = "combobox">
      <select id="selected-source">
        <option>-- Select a Source --</option>
        <option v-for="source in sources" v-bind:key="source.id">{{source}}</option>
      </select>
    </div> 

    <div class="title">Language</div>
    <div class = "combobox">
      <select id="selected-language">
        <option>-- Select a Language --</option>
        <option v-for="language in languages" v-bind:key="language.id">{{language}}</option>
      </select>
    </div>     

    <div class="title">From</div>
    <div class = "combobox"><input id="selected-start-date" type="date"></div>

    <div class="title">To</div>
    <div class = "combobox"><input id="selected-end-date" type="date"></div>

    <button v-on:click="sendRequest()">LAUNCH ANALYSIS</button>
    <button v-on:click="get()">GET</button>           
  </div>
</template>

<script>
//import axios from 'axios'
import $ from 'jquery'
//import {eventBus} from "../main.js"

export default {
  name: 'GlobalSettings',

  data: function() {
    return {
      'selected_country' : '', 
      'selected_source' : '', 
      'selected_language' : '', 
      'selected_start_date' : '', 
      'selected_end_date' : '', 
      'server_response' : [],

      'sources' : ['Twitter','Facebook'],
      'languages' : ["English","French"],
      'countries' : ['Ghana','Qatar','Angola','Macedonia, Republic of','Togo','Turkey','Aruba','Mali','New Zealand','Saint Vincent and Grenadines','Saint-Martin (French part)','Afghanistan','Antigua and Barbuda','Japan','US Minor Outlying Islands','Belgium','Georgia','Libya','Mauritania','Iraq','Niue','Sudan','Wallis and Futuna Islands','Albania','Anguilla','Costa Rica','Croatia','Guernsey','Kenya','Namibia','Netherlands Antilles','Brazil','Dominica','India','Christmas Island','South Georgia and the South Sandwich Islands','Moldova','Mauritius','Poland','Bhutan','Greenland','Guinea-Bissau','Kuwait','Malawi','Burkina Faso','Cuba','French Southern Territories','Malaysia','United States of America','Jamaica','Norfolk Island','Pitcairn','Suriname','Uganda','Israel','Macao, SAR China','New Caledonia','Nicaragua','South Sudan','Azerbaijan','Bulgaria','Comoros','Rwanda','British Virgin Islands','Romania','Andorra','Belarus','Equatorial Guinea','Kyrgyzstan','Lithuania','Slovakia','Denmark','Marshall Islands','Seychelles','Svalbard and Jan Mayen Islands','Cameroon','Jordan','Venezuela (Bolivarian Republic)','Ethiopia','Palau','Armenia','Bermuda','Central African Republic','Germany','Barbados','Monaco','Netherlands','Swaziland','Tonga','Algeria','Guadeloupe','Papua New Guinea','China','Cocos (Keeling) Islands','Hong Kong, SAR China','Iceland','Tokelau','Bouvet Island','Greece','Nauru','Sao Tome and Principe','Paraguay','Republic of Kosovo','Austria','Bolivia','Zimbabwe','Colombia','Turkmenistan','Bosnia and Herzegovina','Congo (Kinshasa)','Cape Verde','Guinea','Iran, Islamic Republic of','Malta','Vanuatu','Timor-Leste','Czech Republic','Sierra Leone','South Africa','Cambodia','Saint Helena','Saint Pierre and Miquelon','Switzerland','Viet Nam','Côte d\'Ivoire','Djibouti','Estonia','Indonesia','Norway','Argentina','Botswana','Eritrea','Virgin Islands, US','Western Sahara','Guyana','Micronesia, Federated States of','San Marino','Burundi','Cayman Islands','Congo (Brazzaville)','Thailand','Portugal','Benin','Guatemala','Panama','United Arab Emirates','El Salvador','Gibraltar','Lebanon','Mongolia','Liechtenstein','Palestinian Territory','Slovenia','Zambia','Liberia','Réunion','Singapore','Taiwan, Republic of China','Tanzania, United Republic of','Guam','Australia','Bahrain','Canada','Chile','Puerto Rico','Ukraine','Bahamas','Holy See (Vatican City State)','Mexico','British Indian Ocean Territory','Turks and Caicos Islands','Fiji','Mozambique','Tajikistan','Trinidad and Tobago','Haiti','Madagascar','Peru','Solomon Islands','Uruguay','Faroe Islands','Heard and Mcdonald Islands','Senegal','Serbia','Dominican Republic','Falkland Islands (Malvinas)','Myanmar','Nigeria','Uzbekistan','Sri Lanka','Gambia','Italy','Korea (North)','Korea (South)','Samoa','Bangladesh','Montenegro','Morocco','Niger','Saudi Arabia','Cyprus','Gabon','Kiribati','Oman','Saint Lucia','Isle of Man','Kazakhstan','Mayotte','Chad','Egypt','Honduras','Hungary','Ireland','American Samoa','Cook Islands','Ecuador','France','Nepal','Luxembourg','Philippines','Sweden','Antarctica','Brunei Darussalam','French Polynesia','Pakistan','Northern Mariana Islands','Saint-Barthélemy','Somalia','Spain','Tunisia','United Kingdom','ALA Aland Islands','Finland','Jersey','Lao PDR','Russian Federation','Yemen','Belize','French Guiana','Latvia','Maldives','Syrian Arab Republic (Syria)','Tuvalu','Grenada','Lesotho','Martinique','Montserrat','Saint Kitts and Nevis']

    }
  },

  methods : {
    sendRequest: function () {
      //Save the parameters
      this.selected_country = document.getElementById("selected-country").value;
      this.selected_source = document.getElementById("selected-source").value.toLowerCase();
      this.selected_language = document.getElementById("selected-language").value;
      this.selected_start_date = document.getElementById("selected-start-date").value;
      this.selected_end_date = document.getElementById("selected-end-date").value;

      var lang_converter = {'French':'fr','English':'en'};
      this.selected_language = lang_converter[this.selected_language];
      //Prepare the json object that will serve as the HTTP POST Request's body
      var request_body = JSON.stringify(
      {
        "country":this.selected_country,
        "source":this.selected_source,
        "lang":this.selected_language,
        "date_from":this.selected_start_date,
        "date_to":this.selected_end_date
      })

      //Launch the HTTP POST Request to the server    
      $.post( "http://127.0.0.1:8000/collector/", request_body)
          .done(function( data) {
            alert( "[GlobalSettings]Data Loaded: " + JSON.stringify(data) );
            //eventBus.$emit('launchDefaultAnalysis');

          });
          /*
      $.ajaxSetup({
          crossDomain: true,
          xhrFields: {
              withCredentials: true
          }
      });   
      */         
      
      
    },
    get: function () {
      //Launch the HTTP POST Request to the server
      $.get( "http://127.0.0.1:8000/access/")
          .done(function( data ) {
            alert( "Data Loaded: " + JSON.stringify(data) );
          });      
    },    
  },

};





</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .container-2 {
    display:flex;
    justify-content:space-between;
    background-color: #5D9DC1;
    padding:20px;
  }

  .title {
    color:white;
    font-size:20px;
  }

  .combobox select, input {
    width:150px;
    height:30px;
    background-color:#EEEEEE;
    border: transparent;
    border-radius:6px;
  } 

  button {
    background-color:#FFFFFF;
    font-weight:bold;
    color:#5D9DC1;
    border: transparent;
    border-radius:6px;
  }


</style>

import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-flex-layout/iron-flex-layout-classes.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/iron-icons/editor-icons.js';
import '@polymer/iron-collapse/iron-collapse.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-input/paper-input.js';

import '../shared-styles.js';
import '../homecon-edit-dialog.js';
import './base-status-light.js';
import './base-slider.js';


class WidgetShading extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles iron-flex iron-flex-alignment">
        :host{
          display: inline-block;
          position: relative;
          width: 100%;
        }
        .button {
          text-transform: none;
          //width: 60px;
          padding: 0px;
        }
        .icon{
          width: 60px;
          height: 60px;
        }
        .label{
          font-size: 16px;
          font-weight: 700;
        }
        .toggle{
          margin-top: -15px;
        }
        .details{
          margin-top: 5px;
          margin-bottom: 30px;
          margin-right: 30px;
        }
        paper-toggle-button{
          margin-right: 20px;
        }
        .edit{
          position: absolute;
          top: -10px;
          right: -10px;
          color: var(--button-text-color);
        }
      </style>

      <div class="horizontal layout">
        <div>
          <div class="clickable horizontal layout start-justified center" on-tap="open_shading">
            <img class="icon" src="[[_parseIcon(iconOpen)]]">
          </div>
        </div>
        <div class="flex">
          <div class="vertical layout center-justified">
            <div class="label">{{label}}</div>
            <base-slider key="{{state}}" min="{{positionOpen}}" max="{{positionClosed}}"></base-slider>
          </div>
        </div>
        <div>
          <div class="clickable horizontal layout start-justified center" on-tap="close_shading">
            <img class="icon" src="[[_parseIcon(iconClosed)]]">
          </div>
        </div>
      </div>

      <div class="horizontal layout toggle">
          <div class="flex"></div>
          <iron-icon on-tap="_toggleCollapse" icon="{{_collapseIcon(detailsOpened)}}"></iron-icon>
      </div>

      <iron-collapse id="details" opened="{{detailsOpened}}">
          <div class="horizontal layout details">
              <div class="flex"></div>
              <paper-toggle-button checked="{{auto}}">Auto</paper-toggle-button>
              <paper-toggle-button checked="{{overrideStatus}}">Override</paper-toggle-button>
          </div>
      </iron-collapse>


      <div class="edit" hidden="{{!edit}}">
          <paper-icon-button icon="editor:mode-edit" noink="true" on-tap="openEditDialog"></paper-icon-button>
      </div>

      <homecon-edit-dialog id="editDialog" on-save="save">
        <template is="dom-if" if="{{edit}}">
          <paper-input label="Label:" value="{{newLabel}}"></paper-input>
          <select-component id="componentSelect" path="{{newPath}}"></select-component>
          <paper-input label="value on:" value="{{newValueOn}}"></paper-input>
          <paper-input label="value off:" value="{{newValueOff}}"></paper-input>
          <homecon-icon-select icon="{{newIcon}}"></homecon-icon-select>
          <paper-input label="color on:" value="{{newColorOn}}"></paper-input>
          <paper-input label="color off:" value="{{newColorOff}}"></paper-input>
          <paper-button on-tap="delete">Delete</paper-button>
        </template>
      </homecon-edit-dialog>
    `;
  }

  static get properties() {
    return {
      label: {
        type: String,
        value: 'new shading'
      },
      state: {
        type: Number,
      },
      positionOpen: {
        type: Number,
        value: 0
      },
      positionClosed: {
        type: Number,
        value: 1
      },
      iconOpen: {
        type: String,
        value: 'fts_shutter_10'
      },
      iconClosed: {
        type: String,
        value: 'fts_shutter_100'
      },
      edit: {
        type: Boolean,
        value: false
      },
      classes: {
        type: String,
        value: 'fullwidth',
      },
    };
  }

  open_shading(){
    window.homeconWebSocket.send({'event': 'state_value', 'data': {'id': this.state, 'value': this.positionOpen}})
  }

  close_shading(){
    window.homeconWebSocket.send({'event': 'state_value', 'data': {'id': this.state, 'value': this.positionClosed}})
  }

  _parseIcon(icon){
    if(icon==''){
      return '/images/icon/ffffff/blank.png';
    }
    else{
      return '/images/icon/ffffff/'+ icon +'.png';
    }
  }

  _collapseIcon(detailsOpened){
    if(detailsOpened){
      return 'expand-less';
    }
    else{
      return 'expand-more';
    }
  }

  _toggleCollapse(){
    this.$.details.toggle()
  }

}

window.customElements.define('widget-shading', WidgetShading);

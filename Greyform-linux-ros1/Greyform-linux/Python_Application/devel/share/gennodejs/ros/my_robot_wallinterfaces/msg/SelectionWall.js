// Auto-generated. Do not edit!

// (in-package my_robot_wallinterfaces.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------

class SelectionWall {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.wallselection = null;
      this.typeselection = null;
      this.sectionselection = null;
      this.picked_position = null;
    }
    else {
      if (initObj.hasOwnProperty('wallselection')) {
        this.wallselection = initObj.wallselection
      }
      else {
        this.wallselection = 0;
      }
      if (initObj.hasOwnProperty('typeselection')) {
        this.typeselection = initObj.typeselection
      }
      else {
        this.typeselection = '';
      }
      if (initObj.hasOwnProperty('sectionselection')) {
        this.sectionselection = initObj.sectionselection
      }
      else {
        this.sectionselection = 0;
      }
      if (initObj.hasOwnProperty('picked_position')) {
        this.picked_position = initObj.picked_position
      }
      else {
        this.picked_position = [];
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type SelectionWall
    // Serialize message field [wallselection]
    bufferOffset = _serializer.int32(obj.wallselection, buffer, bufferOffset);
    // Serialize message field [typeselection]
    bufferOffset = _serializer.string(obj.typeselection, buffer, bufferOffset);
    // Serialize message field [sectionselection]
    bufferOffset = _serializer.int32(obj.sectionselection, buffer, bufferOffset);
    // Serialize message field [picked_position]
    bufferOffset = _arraySerializer.int32(obj.picked_position, buffer, bufferOffset, null);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type SelectionWall
    let len;
    let data = new SelectionWall(null);
    // Deserialize message field [wallselection]
    data.wallselection = _deserializer.int32(buffer, bufferOffset);
    // Deserialize message field [typeselection]
    data.typeselection = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [sectionselection]
    data.sectionselection = _deserializer.int32(buffer, bufferOffset);
    // Deserialize message field [picked_position]
    data.picked_position = _arrayDeserializer.int32(buffer, bufferOffset, null)
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += _getByteLength(object.typeselection);
    length += 4 * object.picked_position.length;
    return length + 16;
  }

  static datatype() {
    // Returns string type for a message object
    return 'my_robot_wallinterfaces/SelectionWall';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'f6985e46a2e326f422d9f77fb3681bba';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    int32 wallselection
    string typeselection
    int32 sectionselection
    int32[] picked_position
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new SelectionWall(null);
    if (msg.wallselection !== undefined) {
      resolved.wallselection = msg.wallselection;
    }
    else {
      resolved.wallselection = 0
    }

    if (msg.typeselection !== undefined) {
      resolved.typeselection = msg.typeselection;
    }
    else {
      resolved.typeselection = ''
    }

    if (msg.sectionselection !== undefined) {
      resolved.sectionselection = msg.sectionselection;
    }
    else {
      resolved.sectionselection = 0
    }

    if (msg.picked_position !== undefined) {
      resolved.picked_position = msg.picked_position;
    }
    else {
      resolved.picked_position = []
    }

    return resolved;
    }
};

module.exports = SelectionWall;

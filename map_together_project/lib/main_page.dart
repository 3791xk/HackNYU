import 'package:flutter/material.dart';
import 'search_info.dart'; // Importing the SearchInfo widget
import 'map_display.dart'; // Importing the MapDisplay widget

class MainPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('GridView Example'),
      ),
      body: GridView.count(
        crossAxisCount: 1,
        children: <Widget>[
          Row(
            children: <Widget>[
              Expanded(
                child: SearchInfo(),
              ),
            ],
          ),
          Row(
            children: <Widget>[
              Expanded(
                child: MapDisplay(),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

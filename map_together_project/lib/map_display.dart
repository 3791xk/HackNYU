import 'package:flutter/material.dart';

class MapDisplay extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.green,
      child: Center(
        child: Text(
          'Map Display',
          style: TextStyle(fontSize: 24, color: Colors.white),
        ),
      ),
    );
  }
}

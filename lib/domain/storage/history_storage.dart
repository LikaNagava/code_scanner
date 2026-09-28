import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/scan_result.dart';

class HistoryStorage {
  static const String _key = 'scan_history_v1';
  static const int _limit = 10;

  Future<List<ScanResult>> load() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final content = prefs.getString(_key);
      if (content == null || content.isEmpty) return [];
      final data = jsonDecode(content) as List<dynamic>;
      return data
          .map((e) => ScanResult.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<void> save(List<ScanResult> items) async {
    final prefs = await SharedPreferences.getInstance();
    final trimmed = items.take(_limit).toList();
    await prefs.setString(
      _key,
      jsonEncode(trimmed.map((e) => e.toJson()).toList()),
    );
  }

  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}
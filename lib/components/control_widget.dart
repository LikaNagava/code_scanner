import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../domain/bloc/scanner/scanner_bloc.dart';
import '../screens/history/history_screen.dart';
import '../screens/result/result_screen.dart';
import '../screens/scanner/scanner_screen.dart';
import 'custom_app_bar.dart';
import '../domain/localization.dart';
import 'custom_bottom_navigation_bar.dart';

class ControlWidget extends StatefulWidget {
  const ControlWidget({super.key});

  @override
  State<ControlWidget> createState() => _ControlWidgetState();
}

class _ControlWidgetState extends State<ControlWidget> {
  int _selectedIndex = 1;
  bool _isRussian = true;
  static const String _langKey = 'app_language';
  AppStrings get _strings => _isRussian ? AppStrings.ru : AppStrings.en;
  final ImagePicker _picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _loadLanguage();
    context.read<ScannerBloc>().add(LoadHistoryEvent());
  }
  Future<void> _loadLanguage() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(_langKey);
    if (saved != null && mounted) {
      setState(() {
        _isRussian = saved == 'ru';
      });
    }
  }

  Future<void> _toggleLanguage() async {
    setState(() => _isRussian = !_isRussian);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_langKey, _isRussian ? 'ru' : 'en');
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<ScannerBloc, ScannerState>(
      listenWhen: (prev, curr) =>
      curr is ScannerResultState || curr is ScannerErrorState,
      listener: (context, state) {
        if (state is ScannerResultState) {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => ResultScreen(
                result: state.result,
                strings: _strings,
              ),
            ),
          );
        } else if (state is ScannerErrorState) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(state.message),
              backgroundColor: Colors.red,
            ),
          );
        }
      },
      child: Scaffold(
        appBar: CustomAppBar(
          isRussian: _isRussian,
          onToggleLanguage: _toggleLanguage,
        ),
        body: _buildBody(),
        bottomNavigationBar: CustomBottomNavigationBar(
          currentIndex: _selectedIndex,
          strings: _strings,
          onTap: (i) {
            setState(() => _selectedIndex = i);
            if (i == 0) {
              context.read<ScannerBloc>().add(LoadHistoryEvent());
            }
          },
        ),
      ),
    );
  }

  Widget _buildBody() {
    switch (_selectedIndex) {
      case 0:
        return HistoryScreen(strings: _strings);
      case 1:
        return ScannerScreen(
          strings: _strings,
          onPickCamera: () => _pick(ImageSource.camera),
        );
      case 2:
        WidgetsBinding.instance.addPostFrameCallback((_) {
          _pick(ImageSource.gallery);
          setState(() => _selectedIndex = 1);
        });
        return ScannerScreen(
          strings: _strings,
          onPickCamera: _noop,
        );
      default:
        return const SizedBox.shrink();
    }
  }

  static void _noop() {}

  Future<void> _pick(ImageSource source) async {
    try {
      final xfile = await _picker.pickImage(
        source: source,
        imageQuality: 90,
        maxWidth: 1600,
      );
      if (xfile == null || !mounted) return;
      context.read<ScannerBloc>().add(RecognizeImageEvent(xfile));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Не удалось выбрать файл. Попробуйте ещё раз.'),
        ),
      );
    }
  }
}
import 'package:flutter/material.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final bool isRussian;
  final VoidCallback onToggleLanguage;

  const CustomAppBar({
    super.key,
    this.isRussian = true,
    required this.onToggleLanguage,
  });

  @override
  Size get preferredSize => const Size.fromHeight(90);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      backgroundColor: Colors.transparent,
      elevation: 0,
      automaticallyImplyLeading: false,
      toolbarHeight: 90,
      titleSpacing: 0,
      title: const SizedBox.shrink(),
      flexibleSpace: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF61A4A4), Color(0xFF225B77)],
            begin: Alignment.centerLeft,
            end: Alignment.centerRight,
          ),
        ),
        child: SafeArea(
          bottom: false,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Image.asset(
                  'assets/icons/logo.png',
                  width: 60,
                  height: 60,
                  fit: BoxFit.contain,
                ),
                const SizedBox(width: 5),
                const Text(
                  'CODE\nSCANNER',
                  style: TextStyle(
                    fontSize: 18,
                    height: 1.0,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 1.5,
                    color: Colors.white,
                  ),
                ),
                const Spacer(),
                Text(
                  'RU',
                  style: TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 15,
                    color: isRussian ? Colors.white : Colors.white54,
                  ),
                ),
                const SizedBox(width: 10),
                GestureDetector(
                  onTap: onToggleLanguage,
                  behavior: HitTestBehavior.opaque,
                  child: Image.asset(
                    isRussian
                        ? 'assets/icons/toggle_ru.png'
                        : 'assets/icons/toggle_en.png',
                    width: 48,
                    height: 26,
                    fit: BoxFit.contain,
                  ),
                ),
                const SizedBox(width: 10),
                Text(
                  'EN',
                  style: TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 15,
                    color: isRussian ? Colors.white54 : Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
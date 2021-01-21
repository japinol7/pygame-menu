"""
pygame-menu
https://github.com/ppizarror/pygame-menu

TEST DECORATOR
Decorator API.

License:
-------------------------------------------------------------------------------
The MIT License (MIT)
Copyright 2017-2021 Pablo Pizarro R. @ppizarror

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
-------------------------------------------------------------------------------
"""

__all__ = ['DecoratorTest']

import copy
import timeit
import unittest
import pygame
import pygame_menu
from test._utils import MenuUtils, surface

# Configure the tests
TEST_TIME_DRAW = False


class DecoratorTest(unittest.TestCase):

    @staticmethod
    def test_time_draw() -> None:
        """
        This test the time that takes to draw the decorator surface with several decorations.
        """
        if not TEST_TIME_DRAW:
            return
        widg = pygame_menu.widgets.NoneWidget()
        deco = widg.get_decorator()
        deco.cache = True
        for i in range(10000):
            deco.add_pixel(1, 2, (0, 0, 0))

        # (100) no cache, 0.214
        # (100) with cache, 0.646
        # (250) no cache, 0.467
        # (250) with cache, 0.594
        # (300) no cache, 0.581
        # (300) with cache, 0.606
        # (400) no cache, 0.82
        # (400) with cache, 0.638
        # (500) no cache, 1.087
        # (500) with cache, 0.601
        # (750) no cache, 1.484
        # (750) with cache, 0.664
        # (1.000) no cache, 2.228
        # (1.000) with cache, 0.615
        # (10.000) no cache, 20.430
        # (10.000) with cache, 0.599
        print('Total decorations', deco._total_decor(), 'Cache', deco.cache)
        total_tests = 10
        t = 0  # total time
        for i in range(total_tests):
            ti = timeit.timeit(lambda: widg.draw(surface), number=1000)
            print('Test', i, 'time:', ti)
            t += ti
        print('Average time:', round(t / total_tests, 3))

    def test_cache(self) -> None:
        """
        Test cache.
        """
        widg = pygame_menu.widgets.NoneWidget()
        deco = widg.get_decorator()
        deco.cache = True

        # Prev
        self.assertEqual(deco._cache_surface['prev'], None)
        self.assertEqual(deco._cache_surface['post'], None)
        deco.add_circle(1, 1, 1, (0, 0, 0), True)
        self.assertEqual(deco._cache_surface['prev'], None)
        self.assertEqual(deco._cache_surface['post'], None)
        deco.draw_prev(surface)
        self.assertNotEqual(deco._cache_surface['prev'], None)
        self.assertEqual(deco._cache_surface['post'], None)
        p = deco._cache_surface['prev']
        deco.add_circle(1, 1, 1, (0, 0, 0), True)
        deco.draw_prev(surface)
        self.assertNotEqual(deco._cache_surface['prev'], p)
        self.assertEqual(deco._cache_surface['post'], None)
        self.assertFalse(deco._cache_needs_update['prev'])
        self.assertFalse(deco._cache_needs_update['post'])
        deco.add_circle(1, 1, 1, (0, 0, 0), True)
        self.assertTrue(deco._cache_needs_update['prev'])
        self.assertFalse(deco._cache_needs_update['post'])
        deco.draw_prev(surface)
        self.assertFalse(deco._cache_needs_update['prev'])
        self.assertFalse(deco._cache_needs_update['post'])
        self.assertEqual(deco._total_decor(), 3)
        deco.remove_all()
        self.assertEqual(deco._total_decor(), 0)
        self.assertFalse(deco._cache_needs_update['prev'])
        self.assertFalse(deco._cache_needs_update['post'])
        deco.draw_prev(surface)
        self.assertFalse(deco._cache_needs_update['prev'])
        self.assertFalse(deco._cache_needs_update['post'])

        # Post
        deco.add_circle(1, 1, 1, (0, 0, 0), False, prev=False)
        self.assertTrue(deco._cache_needs_update['post'])
        self.assertEqual(deco._cache_surface['post'], None)
        deco.draw_post(surface)
        self.assertEqual(deco._total_decor(), 1)
        self.assertFalse(deco._cache_needs_update['post'])
        self.assertNotEqual(deco._cache_surface['post'], None)
        deco.remove_all()
        self.assertEqual(deco._total_decor(), 0)

    def test_copy(self) -> None:
        """
        Test decorator copy.
        """
        widg = pygame_menu.widgets.NoneWidget()
        deco = widg.get_decorator()
        self.assertRaises(Exception, lambda: copy.copy(deco))
        self.assertRaises(Exception, lambda: copy.deepcopy(deco))

    def test_add_remove(self) -> None:
        """
        Test add remove.
        """
        widg = pygame_menu.widgets.NoneWidget()
        deco = widg.get_decorator()

        d = deco._add_none()
        self.assertEqual(len(deco._decor['prev']), 1)
        self.assertEqual(len(deco._decor['post']), 0)
        self.assertEqual(deco._total_decor(), 1)
        assert isinstance(d, str)

        self.assertRaises(IndexError, lambda: deco.remove('none'))
        deco.remove(d)
        self.assertEqual(len(deco._decor['prev']), 0)
        self.assertEqual(len(deco._decor['post']), 0)

        p = deco.add_pixel(1, 1, (1, 1, 1))
        self.assertEqual(len(deco._coord_cache.keys()), 0)
        deco.draw_prev(surface)
        self.assertEqual(len(deco._coord_cache.keys()), 1)
        deco.remove(p)
        self.assertEqual(len(deco._coord_cache.keys()), 0)

    def test_general(self) -> None:
        """
        Test all decorators.
        """
        menu = MenuUtils.generic_menu()
        btn = menu.add_button('Button', None)

        deco = btn.get_decorator()
        poly = [(50, 50), (50, 100), (100, 50)]
        color = (1, 1, 1)

        # Polygon
        self.assertRaises(AssertionError, lambda: deco.add_polygon([(1, 1)], color, True))
        self.assertRaises(AssertionError, lambda: deco.add_polygon([(1, 1)], color, True, 1))
        self.assertRaises(AssertionError, lambda: deco.add_polygon([(1, 1)], color, True, gfx=False))
        # deco.add_filled_polygon(poly, color)
        deco.add_polygon(poly, color, True)
        deco.add_polygon(poly, color, False)
        deco.add_polygon(poly, color, False, gfx=False)
        deco.draw_prev(surface)

        # Circle
        self.assertRaises(AssertionError, lambda: deco.add_circle(1, 1, 0, color, True))
        self.assertRaises(AssertionError, lambda: deco.add_circle(1, 1, 0, color, True, gfx=False))
        self.assertRaises(AssertionError, lambda: deco.add_circle(50, 50, 100, color, True, 1))
        deco.add_circle(1, 1, 100, color, False, 5)
        deco.add_circle(50, 50, 100, color, True)

        # Surface
        img = pygame_menu.baseimage.BaseImage(pygame_menu.baseimage.IMAGE_EXAMPLE_PYGAME_MENU)
        img.scale(0.15, 0.15)
        deco.add_surface(60, 60, img.get_surface(), prev=False)

        # BaseImage
        imgdec = deco.add_baseimage(0, 0, img)

        self.assertEqual(len(deco._coord_cache), 3)
        menu.draw(surface)
        self.assertEqual(len(deco._coord_cache), 7)
        self.assertEqual(deco._coord_cache[imgdec], (299, 173, ((299, 173),)))

        # If widget changes in size, coord cache should change too
        btn.translate(1, 0)
        menu.draw(surface)
        self.assertEqual(deco._coord_cache[imgdec], (300, 173, ((300, 173),)))  # +1

        # As some problems ocurr here, test the position of the widget before padding
        w, h, (x, y) = btn.get_width(), btn.get_height(), btn.get_position()
        self.assertEqual(menu.get_width(widget=True), w)
        self.assertEqual(menu.get_height(widget=True), h)
        wo = (menu.get_height(inner=True) - h) / 2
        self.assertEqual(menu._widget_offset[1], int(wo))
        self.assertEqual(btn.get_rect().center, (int(x + w / 2), int(y + h / 2)))

        # If widget changes padding, the center does not change if pad is equal, so the coord cache must be the same
        # menu.mainloop(surface)
        btn.set_padding(100)
        menu.draw(surface)

        # Test sizing
        self.assertEqual(menu.get_width(widget=True), w + 200)
        self.assertEqual(menu.get_height(widget=True), h + 200)
        wo = (menu.get_height(inner=True) - (h + 200)) / 2
        self.assertEqual(menu._widget_offset[1], int(wo))
        self.assertEqual(btn.get_rect().x, x - 100)
        self.assertEqual(btn.get_rect().y, y - 100)
        self.assertEqual(btn.get_rect().center, (int(x + w / 2), int(y + h / 2)))

        self.assertEqual(deco._coord_cache[imgdec], (300, 173, ((300, 173),)))

        # Padding left is 0, then widget center changes
        btn.set_padding((100, 100, 100, 0))
        menu.draw(surface)
        self.assertEqual(deco._coord_cache[imgdec], (300, 173, ((300, 173),)))
        btn.set_padding((100, 0, 100, 0))
        menu.draw(surface)
        # menu.mainloop(surface)
        self.assertEqual(deco._coord_cache[imgdec], (300, 173, ((300, 173),)))

        # Text
        self.assertRaises(ValueError, lambda: deco.add_text(100, 200, 'nice', pygame_menu.font.FONT_8BIT, 0, color))
        deco.add_text(-150, 0, 'nice', pygame_menu.font.FONT_8BIT, 20, color, centered=True)
        menu.draw(surface)

        # Ellipse
        self.assertRaises(AssertionError, lambda: deco.add_ellipse(0, 0, 0, 0, color, True))
        deco.add_ellipse(-250, 0, 110, 150, (255, 0, 0), True)
        deco.add_ellipse(-250, 0, 110, 150, (255, 0, 0), False)

        # Callable
        test = [False]

        def fun(surf, obj: 'pygame_menu.widgets.Button') -> None:
            """
            Test callable decoration.
            """
            test[0] = True
            assert isinstance(surf, pygame.Surface)
            assert isinstance(obj, pygame_menu.widgets.Button)

        deco.add_callable(fun)
        self.assertFalse(test[0])
        btn.draw(surface)
        self.assertTrue(test[0])

        # Textued polygon
        deco.add_textured_polygon(((10, 10), (100, 100), (120, 10)), img)

        # Arc
        deco.add_arc(0, 0, 50, 0, 100, (0, 255, 0), True)
        deco.add_arc(0, 0, 50, 0, 100, (0, 255, 0), False)

        # Pie
        deco.add_pie(0, 0, 50, 0, 100, (0, 255, 0))

        # Bezier
        deco.add_bezier(((100, 100), (0, 0), (0, -100)), (70, 10, 100), 10)

        # Rect
        deco.add_rect(200, 30, pygame.Rect(0, 0, 100, 300), (0, 0, 100))
        deco.add_rect(0, 30, pygame.Rect(0, 0, 100, 300), (100, 0, 100), width=10)

        # Pixel
        for i in range(5):
            for j in range(5):
                deco.add_pixel(10 * i, 10 * j, color)

        # Line
        deco.add_line((10, 10), (100, 100), (45, 180, 34), 10)
        deco.add_hline(1, 2, 3, color)
        deco.add_vline(1, 2, 3, color)

        menu.draw(surface)
        # menu.mainloop(surface)
        deco.remove_all()

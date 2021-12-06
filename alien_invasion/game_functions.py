import sys
import pygame
from bullet import Bullet
from alien import Alien
from time import sleep

"""监视键盘和鼠标"""
def check_keydown_events(event,ai_settings,screen,ship,bullets):

    if event.key == pygame.K_RIGHT:
        ship.move_right = True

    elif event.key == pygame.K_LEFT:
        ship.move_left = True

    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings,screen,ship,bullets)

    elif event.key == pygame.K_q:
        sys.exit()

def check_keyup_events(event,ship):

        if event.key == pygame.K_RIGHT:
            ship.move_right = False

        elif event.key == pygame.K_LEFT:
            ship.move_left = False

def check_events(ai_settings,screen,stats,sb,play_button,ship,
                aliens,bullets):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event,ai_settings,screen,ship,bullets)

        elif event.type == pygame.KEYUP:
            check_keyup_events(event,ship)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x,mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings,screen,stats,sb,play_button,
                ship,aliens,bullets,mouse_x,mouse_y)

def check_play_button(ai_settings,screen,stats,sb,play_button,ship,
        aliens,bullets,mouse_x,mouse_y):
    button_clicked =play_button.rect.collidepoint(mouse_x,mouse_y)
    if button_clicked and not stats.game_active:
        ai_settings.initialize_dynamic_settings()

        pygame.mouse.set_visible(False)

        stats.reset_stats()
        stats.game_active = True

        sb.prep_score()
        sb.prep_score()
        sb.prep_level()
        sb.prep_ships()

        aliens.empty()
        bullets.empty()

        create_fleet(ai_settings,screen,ship,aliens)
        ship.center_ship()

def update_screen(ai_settings, stats, screen, sb, ship, aliens, bullets,
        play_button):
    """每次循环时重新绘制屏幕"""
    screen.fill(ai_settings.bg_color)
    ship.blitme()
    sb.show_score()

    for bullet in bullets.sprites():
        bullet.draw_bullet()

    aliens.draw(screen)

    if not stats.game_active:
        play_button.draw_button()

    """展示最近绘制的屏幕"""
    pygame.display.flip()

def update_bullets(ai_settings,stats,screen,sb,ship,aliens, bullets):
    bullets.update()
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    check_bullet_alien_collisions(ai_settings,stats,screen,sb,
        ship,aliens,bullets)

def check_bullet_alien_collisions(ai_settings,stats,screen,sb,ship,
        aliens,bullets):
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats,sb)

    if len(aliens) == 0:
        bullets.empty()
        ai_settings.increase_speed()
        stats.level += 1
        sb.prep_level()
        create_fleet(ai_settings,screen,ship,aliens)

def fire_bullet(ai_settings,screen,ship,bullets):
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)

def get_number_aliens_x(ai_settings,alien_width):
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x/(2 * alien_width))
    return number_aliens_x

def get_number_aliens_y(ai_settings,ship_height,alien_height):
    available_space_y = (ai_settings.screen_height -
                            (alien_height * 3) - ship_height)
    number_aliens_y = int(available_space_y/(2 * alien_height))
    return number_aliens_y

def create_alien(ai_settings,screen,aliens,alien_number_x,
    alien_number_y):
    alien = Alien(ai_settings,screen)
    alien.rect.x = (alien.rect.width
    + 2 * alien.rect.width * alien_number_x)
    alien.rect.y = (alien.rect.height
    + 2 * alien.rect.height * alien_number_y)
    aliens.add(alien)

def create_fleet(ai_settings,screen,ship,aliens):
    alien = Alien(ai_settings,screen)
    number_aliens_x = get_number_aliens_x(ai_settings,alien.rect.width)
    number_aliens_y = get_number_aliens_y(ai_settings,
        ship.rect.height,alien.rect.height)

    for alien_number_y in range(number_aliens_y):
        for alien_number_x in range(number_aliens_x):
            create_alien(ai_settings,screen,aliens,alien_number_x,
            alien_number_y)

def check_fleet_edges(ai_settings,aliens):
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings,aliens)
            break

def change_fleet_direction(ai_settings,aliens):
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed

    ai_settings.fleet_direction *= -1

def update_aliens(ai_settings,stats,sb,screen,ship,aliens,bullets):
    check_fleet_edges(ai_settings,aliens)
    aliens.update()

    if pygame.sprite.spritecollideany(ship,aliens):
        print("Ship hit!!!""")
        ship_hit(ai_settings,stats,screen,sb,ship,aliens,bullets)

    check_aliens_bottom(ai_settings, stats, screen,sb,ship,aliens,bullets)

def ship_hit(ai_settings,stats,screen,sb,ship,aliens,bullets):

    if stats.ships_left > 0:
        stats.ships_left -= 1
        sb.prep_ships()

        aliens.empty()
        bullets.empty()

        create_fleet(ai_settings,screen,ship,aliens)
        ship.center_ship()

        """暂停"""
        sleep(0.5)

    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)

def check_aliens_bottom(ai_settings, stats, screen,sb,ship,aliens,bullets):

    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            ship_hit(ai_settings,stats,screen,sb,ship,aliens,bullets)
            break

def check_high_score(stats,sb):
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()
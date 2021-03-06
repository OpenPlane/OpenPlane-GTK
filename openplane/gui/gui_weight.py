#!/usr/bin/env python3
# coding: utf-8

# Made by Louis Etienne

from gi.repository import Gtk
from openplane.core.Plane import *
from openplane.gui.gui_hangar import *
import matplotlib.pyplot as plt
from openplane import config
from openplane import text
import numpy as np
import glob
import os


class WeightWindow:

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(config.weight)

        handlers = {
            'on_spinButton_changed': self.on_spin_changed,
            'on_save_clicked': self.on_save_clicked,
            'on_addPlane_clicked': self.on_addPlane_clicked,
            'on_preview_toggled': self.on_preview_toggled,
            'on_quit_clicked': self.app_quit,
            'on_delete_event': self.app_quit
        }

        builder.connect_signals(handlers)

        self.window = builder.get_object('mainWindow')
        self.width, self.height = self.window.get_size()
        self.window.set_icon_from_file(config.icon_path)

        main_layout = builder.get_object('mainLayout')
        self.planes_list = Gtk.ListStore(str, str)

        plane_chooser = Gtk.ComboBox.new_with_model(self.planes_list)
        plane_chooser.connect('changed', self.on_plane_chooser_changed)
        renderer_text = Gtk.CellRendererText()
        plane_chooser.pack_start(renderer_text, True)
        plane_chooser.add_attribute(renderer_text, "text", 0)
        main_layout.attach(plane_chooser, 1, 0, 1, 1)

        self.btn_save = builder.get_object('save')
        self.btn_save.set_sensitive(False)

        self.preview_box = builder.get_object('previewBtn')
        self.preview = builder.get_object('preview')
        self.clear_preview()

        self.masse_std1 = builder.get_object('masseVideStd1')
        self.masse_std2 = builder.get_object('masseVideStd2')
        self.options1 = builder.get_object('options1')
        self.options2 = builder.get_object('options2')

        self.pass_av1 = builder.get_object('passagersAv1')
        self.pass_av2 = builder.get_object('passagersAv2')
        self.pass_ar1 = builder.get_object('passagersAr1')
        self.pass_ar2 = builder.get_object('passagersAr2')
        self.carbu1 = builder.get_object('carbu1')
        self.carbu2 = builder.get_object('carbu2')
        self.bagages1 = builder.get_object('bagages1')
        self.bagages2 = builder.get_object('bagages2')

        self.masse_vide_std_lab = builder.get_object('masseVideStd')
        self.options_lab = builder.get_object('options')
        self.masse_vide_lab1 = builder.get_object('masseVideBase1')
        self.bdl_masse_vide_lab = builder.get_object('bdlMasseVide')
        self.masse_vide_lab2 = builder.get_object('masseVideBase2')
        self.passagers_av_lab = builder.get_object('passagerAv')
        self.passagers_ar_lab = builder.get_object('passagersAr')
        self.carbu_lab = builder.get_object('carbu')
        self.bagages_lab = builder.get_object('bagages')
        self.masse_avc_carbu_lab = builder.get_object('masseAvcCarbu')
        self.masse_sns_carbu_lab = builder.get_object('masseSnsCarbu')
        self.moment_avc_carbu_lab = builder.get_object('momentAvcCarbu')
        self.moment_sns_carbu_lab = builder.get_object('momentSnsCarbu')
        self.bdl_avc_carbu_lab = builder.get_object('bdlAvecCarbu')
        self.bdl_sns_carbu_lab = builder.get_object('bdlSansCarbu')

        self.update_plane_list()
        self.calc_label()

    def update_plane_list(self):
        self.planes_list.clear()
        for plane_file in glob.glob('{}*{}'.format(config.planes_folder,
                                                   config.planes_ext)):
                plane = os.path.basename(plane_file)
                self.planes_list.append([os.path.splitext(plane)[0],
                                         plane_file])

    def import_plane_values(self, plane):
        self.masse_std1.set_value(plane.empty_mass)
        self.masse_std2.set_value(plane.empty_bdl)
        self.options1.set_value(plane.options_mass)
        self.options2.set_value(plane.options_bdl)

        self.pass_av2.set_value(plane.pass_av)
        self.pass_ar2.set_value(plane.pass_ar)
        self.carbu2.set_value(plane.fuel)
        self.bagages2.set_value(plane.baggage)

        if self.masse_std2.get_value() > 0:
            self.calc_label()

    def on_addPlane_clicked(self, btn):
        hangar = HangarDialog()
        hangar.dialog.run()
        self.update_plane_list()

    def on_plane_chooser_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            name, path = model[tree_iter][:2]

            self.clear_preview()

            self.plane = Plane()
            self.plane.import_plane(path)
            self.window.set_title(text.weight_title.format(name))

            self.btn_save.set_sensitive(True)
            self.masse_std1.set_editable(True)
            self.masse_std2.set_editable(True)
            self.options1.set_editable(True)
            self.options2.set_editable(True)
            self.pass_av1.set_editable(True)
            self.pass_av2.set_editable(True)
            self.pass_ar1.set_editable(True)
            self.pass_ar2.set_editable(True)
            self.carbu1.set_editable(True)
            self.carbu2.set_editable(True)
            self.bagages1.set_editable(True)
            self.bagages2.set_editable(True)

            self.import_plane_values(self.plane)

    def clear_preview(self):
        self.preview.clear()
        self.window.resize(self.width, self.height)

    def on_save_clicked(self, button):

        dialog = Gtk.FileChooserDialog(text.save_weight, self.window,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_SAVE,
                                        Gtk.ResponseType.OK,
                                        Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL))
        self.add_filters(dialog)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:

            figure_path, figure_ext = os.path.splitext(dialog.get_filename())

            if figure_ext == '':
                figure_ext = '.png'

            figure_name = '{}{}'.format(figure_path, figure_ext)

            self.create_graph(figure_name, self.plane,
                              self.masse_avec_carbu, self.bdl_avec_carbu,
                              self.masse_vide, self.bdl_masse_vide, True)
        else:
            pass

        dialog.destroy()

    def add_filters(self, dialog):
        filter_png = Gtk.FileFilter()
        filter_png.set_name(text.png_files)
        filter_png.add_mime_type("image/png")
        dialog.add_filter(filter_png)

        filter_any = Gtk.FileFilter()
        filter_any.set_name(text.all_files)
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def calc_label(self):
        masse_std = self.masse_std1.get_value() * self.masse_std2.get_value()
        options = self.options1.get_value() * self.options2.get_value()
        pass_av = self.pass_av1.get_value() * self.pass_av2.get_value()
        pass_ar = self.pass_ar1.get_value() * self.pass_ar2.get_value()
        carbu = self.carbu1.get_value() * self.carbu2.get_value()
        bagages = self.bagages1.get_value() * self.bagages2.get_value()

        # Totaux
        self.masse_vide = self.masse_std1.get_value() + \
            self.options1.get_value()

        mmt_masse_vide = masse_std + options

        self.bdl_masse_vide = self.masse_std2.get_value() + \
            self.options2.get_value()

        self.masse_avec_carbu = self.masse_vide + self.pass_av1.get_value() + \
            self.pass_ar1.get_value() + self.bagages1.get_value() + \
            self.carbu1.get_value()

        mmt_avec_carbu = mmt_masse_vide + pass_av + pass_ar + carbu + bagages

        masse_sans_carbu = self.masse_vide + self.pass_av1.get_value() + \
            self.pass_ar1.get_value() + self.bagages1.get_value()

        mmt_sans_carbu = mmt_masse_vide + pass_av + pass_ar + bagages

        self.masse_vide_std_lab.set_text(str(round(masse_std, 3)))
        self.options_lab.set_text(str(round(options, 3)))
        self.masse_vide_lab1.set_text(str(round(self.masse_vide, 3)))
        self.bdl_masse_vide_lab.set_text(str(round(self.bdl_masse_vide, 3)))
        self.masse_vide_lab2.set_text(str(round(mmt_masse_vide, 3)))
        self.passagers_av_lab.set_text(str(round(pass_av, 3)))
        self.passagers_ar_lab.set_text(str(round(pass_ar, 3)))
        self.carbu_lab.set_text(str(round(carbu, 3)))
        self.bagages_lab.set_text(str(round(bagages, 3)))
        self.masse_avc_carbu_lab.set_text(str(round(self.masse_avec_carbu, 3)))
        self.moment_avc_carbu_lab.set_text(str(round(mmt_avec_carbu, 3)))
        self.masse_sns_carbu_lab.set_text(str(round(masse_sans_carbu, 3)))
        self.moment_sns_carbu_lab.set_text(str(round(mmt_sans_carbu, 3)))

        if self.masse_avec_carbu > 0 or masse_sans_carbu > 0:
            self.bdl_avec_carbu = mmt_avec_carbu / self.masse_avec_carbu
            bdl_sans_carbu = mmt_sans_carbu / masse_sans_carbu
            self.bdl_avc_carbu_lab.set_text(str(round(self.bdl_avec_carbu, 3)))
            self.bdl_sns_carbu_lab.set_text(str(round(bdl_sans_carbu, 3)))
        else:
            self.bdl_avc_carbu_lab.set_text(str(0.00))
            self.bdl_sns_carbu_lab.set_text(str(0.00))

    def on_preview_toggled(self, check):
        if check.get_active():
            self.update_preview()
            self.btn_save.set_sensitive(True)
        else:
            self.clear_preview()
            self.btn_save.set_sensitive(False)

    def update_preview(self):
        figure_path = config.preview

        if self.masse_avec_carbu > 0 or self.masse_sans_carbu > 0:
            self.create_graph(figure_path,
                              self.plane,
                              self.masse_avec_carbu,
                              self.bdl_avec_carbu,
                              self.masse_vide,
                              self.bdl_masse_vide)
            self.preview.set_from_file(figure_path)

    def on_spin_changed(self, spin):
        if self.masse_std1.get_value() > 0:
            self.calc_label()
            if self.preview_box.get_active():
                self.update_preview()

    def create_graph(self, figure_path, plane, masse_total, bdl_total,
                     masse_vide, bdl_vide, full=False):
        # Génération du domaine
        dom_x = np.array([plane.p1x, plane.p2x, plane.p3x,
                          plane.p4x, plane.p5x])
        dom_y = np.array([plane.p1y, plane.p2y, plane.p3y,
                          plane.p4y, plane.p5y])

        # On calcule l'équation de droite :
        # y = ax + b
        a = (plane.p3y - plane.p2y) / (plane.p3x - plane.p2x)
        b = (-a * plane.p2x) + plane.p2y

        # Si les points sortent du cadre, on affiche celui-ci en rouge
        if bdl_total < plane.p1x or bdl_total > plane.p5x or \
           (masse_total > (a * bdl_total) + b) or \
           (bdl_total > plane.p3x and masse_total > plane.p3y):
            plt.plot(dom_x, dom_y, color='r', linewidth=2)
        else:
            plt.plot(dom_x, dom_y, color='b', linewidth=1)

        plt.ylim((plane.p1y, plane.p3y + 50))  # Limites en y

        # Catégorie utilitaire
        if plane.utility:
            dom_u_x = np.array([plane.up1x, plane.up2x, plane.up3x,
                                plane.up4x, plane.up5x])
            dom_u_y = np.array([plane.up1y, plane.up2y, plane.up3y,
                                plane.up4y, plane.up5y])

            # On calcule l'équation de droite :
            # y = ax + b
            ua = (plane.up3y - plane.up2y) / (plane.up3x - plane.up2x)
            ub = (-ua * plane.up2x) + plane.up2y

            # Si les points sortent du cadre, on affiche celui-ci en rouge
            if bdl_total < plane.up1x or bdl_total > plane.up5x or \
               (masse_total > (ua * bdl_total) + ub) or \
               (bdl_total > plane.up3x and masse_total > plane.up3y):
                plt.plot(dom_u_x, dom_u_y, 'r--', linewidth=2, color='r')
            else:
                plt.plot(dom_u_x, dom_u_y, 'r--', linewidth=1.5, color='g')

        # Points de centrage
        total_x = np.array([bdl_total, bdl_vide])
        total_y = np.array([masse_total, masse_vide])

        plt.plot(total_x, total_y, color='r', marker='.', markersize=12)

        # Un peu de déco
        plt.xlabel(text.lever_arm)
        plt.ylabel(text.mass)
        plt.grid(True)
        plt.title(text.weight_title.format(plane.matriculation))

        if full:
            # Si l'utilisateur demande d'exporter le graphique, on le met à
            # 100 dpi
            plt.savefig(figure_path)
        else:
            plt.savefig(figure_path, dpi=75)

        plt.clf()  # On ferme la figure actuelle

    def app_quit(self, *args):
        self.window.destroy()

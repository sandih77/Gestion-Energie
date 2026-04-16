from model.Materiel import Appareil
from model.Periode import Periode
from model.Utilisation import Utilisation


class EnergieCalculator:
    MATIN_WINDOW = (6 * 60, 17 * 60)
    FA_WINDOW = (17 * 60, 19 * 60)
    SOIREE_WINDOW = (19 * 60, 6 * 60)

    @staticmethod
    def _period_kind(nom_periode):
        nom = (nom_periode or "").strip().lower()
        if "matin" in nom:
            return "matin"
        if "fa" in nom or "apres" in nom or "apres-midi" in nom or "fin" in nom:
            return "fa"
        if "soir" in nom or "nuit" in nom:
            return "soiree"
        return "autre"

    @staticmethod
    def _time_to_minutes(hhmmss):
        if not hhmmss:
            return 0
        parts = str(hhmmss).split(":")
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        return hours * 60 + minutes

    @staticmethod
    def _minutes_to_hhmm(total_minutes):
        minutes = int(total_minutes) % 1440
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    @staticmethod
    def _normalize_percentage(value, default):
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _split_interval(start_min, end_min):
        if end_min > start_min:
            return [(start_min, end_min)]
        return [(start_min, 1440), (0, end_min)]

    @staticmethod
    def _window_segments(window_start, window_end):
        if window_end > window_start:
            return [(window_start, window_end)]
        return [(window_start, 1440), (0, window_end)]

    @staticmethod
    def _overlap_minutes(a_start, a_end, b_start, b_end):
        start = max(a_start, b_start)
        end = min(a_end, b_end)
        return max(0, end - start)

    @staticmethod
    def _usage_power(utilisation):
        appareil = Appareil.get_by_id(utilisation.appareil_id)
        if appareil is None or appareil.puissance_w is None:
            return 0.0
        return float(appareil.puissance_w)

    @staticmethod
    def _window_energy_wh(utilisations, window_start, window_end):
        total_wh = 0.0
        for utilisation in utilisations:
            power_w = EnergieCalculator._usage_power(utilisation)
            if power_w <= 0:
                continue

            start_min = EnergieCalculator._time_to_minutes(utilisation.heure_debut)
            end_min = EnergieCalculator._time_to_minutes(utilisation.heure_fin)

            for usage_start, usage_end in EnergieCalculator._split_interval(start_min, end_min):
                for window_segment_start, window_segment_end in EnergieCalculator._window_segments(window_start, window_end):
                    overlap_min = EnergieCalculator._overlap_minutes(
                        usage_start,
                        usage_end,
                        window_segment_start,
                        window_segment_end,
                    )
                    if overlap_min > 0:
                        total_wh += power_w * (overlap_min / 60.0)

        return round(total_wh, 2)

    @staticmethod
    def _window_covered_minutes(utilisations, window_start, window_end):
        intervals = []

        for utilisation in utilisations:
            start_min = EnergieCalculator._time_to_minutes(utilisation.heure_debut)
            end_min = EnergieCalculator._time_to_minutes(utilisation.heure_fin)

            for usage_start, usage_end in EnergieCalculator._split_interval(start_min, end_min):
                for window_segment_start, window_segment_end in EnergieCalculator._window_segments(window_start, window_end):
                    overlap_start = max(usage_start, window_segment_start)
                    overlap_end = min(usage_end, window_segment_end)
                    if overlap_start < overlap_end:
                        intervals.append((overlap_start, overlap_end))

        if not intervals:
            return 0

        intervals.sort(key=lambda item: item[0])
        merged = [intervals[0]]

        for current_start, current_end in intervals[1:]:
            last_start, last_end = merged[-1]
            if current_start <= last_end:
                merged[-1] = (last_start, max(last_end, current_end))
            else:
                merged.append((current_start, current_end))

        return sum(end - start for start, end in merged)

    @staticmethod
    def _window_peak_power_w(utilisations, window_start, window_end, extra_loads=None):
        events = []

        for utilisation in utilisations:
            power_w = EnergieCalculator._usage_power(utilisation)
            if power_w <= 0:
                continue

            start_min = EnergieCalculator._time_to_minutes(utilisation.heure_debut)
            end_min = EnergieCalculator._time_to_minutes(utilisation.heure_fin)

            for usage_start, usage_end in EnergieCalculator._split_interval(start_min, end_min):
                for window_segment_start, window_segment_end in EnergieCalculator._window_segments(window_start, window_end):
                    overlap_start = max(usage_start, window_segment_start)
                    overlap_end = min(usage_end, window_segment_end)
                    if overlap_start < overlap_end:
                        events.append((overlap_start, power_w))
                        events.append((overlap_end, -power_w))

        for load in (extra_loads or []):
            load_start, load_end, load_power = load
            if load_power <= 0:
                continue

            for usage_start, usage_end in EnergieCalculator._split_interval(load_start, load_end):
                for window_segment_start, window_segment_end in EnergieCalculator._window_segments(window_start, window_end):
                    overlap_start = max(usage_start, window_segment_start)
                    overlap_end = min(usage_end, window_segment_end)
                    if overlap_start < overlap_end:
                        events.append((overlap_start, load_power))
                        events.append((overlap_end, -load_power))

        if not events:
            return 0.0

        events.sort(key=lambda item: (item[0], item[1]))
        current_power = 0.0
        peak_power = 0.0

        for _, delta in events:
            current_power += delta
            if current_power > peak_power:
                peak_power = current_power

        return round(peak_power, 2)

    @staticmethod
    def get_default_parameters():
        matin_yield = 40.0
        fa_yield = 20.0

        for periode in Periode.get_all():
            kind = EnergieCalculator._period_kind(periode.nom)
            rendement = EnergieCalculator._normalize_percentage(periode.rendement_panneau, None)
            if rendement is None:
                continue
            if kind == "matin":
                matin_yield = rendement
            elif kind == "fa":
                fa_yield = rendement

        return {
            "matin_yield": matin_yield,
            "fa_yield": fa_yield,
            "battery_margin": 50.0,
        }

    @staticmethod
    def _calculate_common_data():
        utilisations = Utilisation.get_all()

        battery_theoretical_wh = EnergieCalculator._window_energy_wh(
            utilisations,
            EnergieCalculator.SOIREE_WINDOW[0],
            EnergieCalculator.SOIREE_WINDOW[1],
        )

        charge_start = EnergieCalculator.MATIN_WINDOW[0]
        charge_end = EnergieCalculator.FA_WINDOW[1]

        matin_minutes = EnergieCalculator._overlap_minutes(
            charge_start,
            charge_end,
            EnergieCalculator.MATIN_WINDOW[0],
            EnergieCalculator.MATIN_WINDOW[1],
        )
        fa_minutes = EnergieCalculator._overlap_minutes(
            charge_start,
            charge_end,
            EnergieCalculator.FA_WINDOW[0],
            EnergieCalculator.FA_WINDOW[1],
        )

        # Batterie: en FA elle charge a 50% de la puissance matin.
        heures_equivalentes_charge = (matin_minutes / 60.0) + ((fa_minutes / 60.0) * 0.5)
        soiree_usage_hours = round(heures_equivalentes_charge, 2)
        battery_charge_power_w = (
            round(battery_theoretical_wh / heures_equivalentes_charge, 2)
            if heures_equivalentes_charge > 0
            else 0.0
        )
        battery_charge_power_fa_w = round(battery_charge_power_w * 0.5, 2)

        battery_charge_start_min = charge_start
        battery_charge_end_min = charge_end
        battery_charge_loads = []
        if battery_charge_power_w > 0 and matin_minutes > 0:
            battery_charge_loads.append(
                (EnergieCalculator.MATIN_WINDOW[0], EnergieCalculator.MATIN_WINDOW[1], battery_charge_power_w)
            )
        if battery_charge_power_fa_w > 0 and fa_minutes > 0:
            battery_charge_loads.append(
                (EnergieCalculator.FA_WINDOW[0], EnergieCalculator.FA_WINDOW[1], battery_charge_power_fa_w)
            )

        panel_morning_theoretical_w = EnergieCalculator._window_peak_power_w(
            utilisations,
            EnergieCalculator.MATIN_WINDOW[0],
            EnergieCalculator.MATIN_WINDOW[1],
            extra_loads=battery_charge_loads,
        )

        panel_fa_theoretical_w = EnergieCalculator._window_peak_power_w(
            utilisations,
            EnergieCalculator.FA_WINDOW[0],
            EnergieCalculator.FA_WINDOW[1],
            extra_loads=battery_charge_loads,
        )

        pic_matin_appareils_w = EnergieCalculator._window_peak_power_w(
            utilisations,
            EnergieCalculator.MATIN_WINDOW[0],
            EnergieCalculator.MATIN_WINDOW[1],
        )

        pic_fa_appareils_w = EnergieCalculator._window_peak_power_w(
            utilisations,
            EnergieCalculator.FA_WINDOW[0],
            EnergieCalculator.FA_WINDOW[1],
        )

        pic_soiree_appareils_w = EnergieCalculator._window_peak_power_w(
            utilisations,
            EnergieCalculator.SOIREE_WINDOW[0],
            EnergieCalculator.SOIREE_WINDOW[1],
        )

        print(panel_fa_theoretical_w / (40.0 / 100.0) / (50.0 / 100.0))

        # Le convertisseur est commun: base sur le pic de puissance theorique du panneau.
        pic_matin_w = panel_morning_theoretical_w
        pic_fa_w = panel_fa_theoretical_w
        # Pas de production panneau en soiree.
        pic_soiree_w = 0.0
        puissance_pic_journee_w = round(max(pic_matin_w, pic_fa_w, pic_soiree_w), 2)
        puissance_convertisseur_w = round(puissance_pic_journee_w * 2.0, 2)

        puissance_pic_journee_appareils_w = round(
            max(pic_matin_appareils_w, pic_fa_appareils_w, pic_soiree_appareils_w),
            2,
        )
        puissance_convertisseur_appareils_w = round(puissance_pic_journee_appareils_w * 2.0, 2)

        return {
            "battery_theoretical_wh": battery_theoretical_wh,
            "soiree_usage_hours": soiree_usage_hours,
            "battery_charge_start": EnergieCalculator._minutes_to_hhmm(battery_charge_start_min),
            "battery_charge_end": EnergieCalculator._minutes_to_hhmm(battery_charge_end_min),
            "battery_charge_power_w": battery_charge_power_w,
            "panel_morning_theoretical_w": panel_morning_theoretical_w,
            "panel_fa_theoretical_w": panel_fa_theoretical_w,
            "pic_matin_w": pic_matin_w,
            "pic_fa_w": pic_fa_w,
            "pic_soiree_w": pic_soiree_w,
            "puissance_pic_journee_w": puissance_pic_journee_w,
            "puissance_convertisseur_w": puissance_convertisseur_w,
            "puissance_convertisseur_appareils_w": puissance_convertisseur_appareils_w,
        }

    @staticmethod
    def calculate_dimensionnement(matin_yield_pct=40.0, fa_yield_pct=20.0, battery_margin_pct=50.0, common_data=None):
        donnees = common_data or EnergieCalculator._calculate_common_data()

        battery_theoretical_wh = donnees["battery_theoretical_wh"]
        soiree_usage_hours = donnees["soiree_usage_hours"]
        battery_charge_power_w = donnees["battery_charge_power_w"]
        panel_morning_theoretical_w = donnees["panel_morning_theoretical_w"]
        panel_fa_theoretical_w = donnees["panel_fa_theoretical_w"]

        matin_yield = max(EnergieCalculator._normalize_percentage(matin_yield_pct, 40.0), 0.0)
        fa_yield = max(EnergieCalculator._normalize_percentage(fa_yield_pct, 20.0), 0.0)
        battery_margin = max(EnergieCalculator._normalize_percentage(battery_margin_pct, 50.0), 0.0)

        panel_morning_practical_w = round(panel_morning_theoretical_w / (matin_yield / 100.0), 2) if matin_yield > 0 else 0.0
        panel_fa_practical_w = round(panel_fa_theoretical_w / (fa_yield / 100.0) / (matin_yield / 100.0), 2) if fa_yield > 0 else 0.0
        print(panel_fa_practical_w)
        battery_charge_practical_w = round(battery_charge_power_w / (matin_yield / 100.0), 2) if matin_yield > 0 else 0.0

        panel_required_w = round(max(panel_morning_practical_w, panel_fa_practical_w), 2)
        battery_practical_wh = round(battery_theoretical_wh * (1.0 + battery_margin / 100.0), 2)
        # battery_practical_wh = round(battery_theoretical_wh / (battery_margin / 100.0), 2)

        return {
            "battery_theoretical_wh": battery_theoretical_wh,
            "battery_practical_wh": battery_practical_wh,
            "battery_margin_pct": battery_margin,
            "soiree_usage_hours": soiree_usage_hours,
            "battery_charge_start": donnees["battery_charge_start"],
            "battery_charge_end": donnees["battery_charge_end"],
            "battery_charge_power_w": battery_charge_power_w,
            "battery_charge_practical_w": battery_charge_practical_w,
            "panel_morning_theoretical_w": panel_morning_theoretical_w,
            "panel_morning_practical_w": panel_morning_practical_w,
            "panel_fa_theoretical_w": panel_fa_theoretical_w,
            "panel_fa_practical_w": panel_fa_practical_w,
            "panel_required_w": panel_required_w,
            "matin_yield_pct": matin_yield,
            "fa_yield_pct": fa_yield,
        }

    @staticmethod
    def calculate_dimensionnement_double(
        p1_matin_yield_pct,
        p1_fa_yield_pct,
        p1_battery_margin_pct,
        p2_matin_yield_pct,
        p2_fa_yield_pct,
        p2_battery_margin_pct,
    ):
        commun = EnergieCalculator._calculate_common_data()

        p1 = EnergieCalculator.calculate_dimensionnement(
            p1_matin_yield_pct,
            p1_fa_yield_pct,
            p1_battery_margin_pct,
            common_data=commun,
        )
        p2 = EnergieCalculator.calculate_dimensionnement(
            p2_matin_yield_pct,
            p2_fa_yield_pct,
            p2_battery_margin_pct,
            common_data=commun,
        )

        return {
            "p1": p1,
            "p2": p2,
            "commun": {
                "pic_matin_w": commun["pic_matin_w"],
                "pic_fa_w": commun["pic_fa_w"],
                "pic_soiree_w": commun["pic_soiree_w"],
                "puissance_pic_journee_w": commun["puissance_pic_journee_w"],
                "puissance_convertisseur_w": commun["puissance_convertisseur_w"],
                "puissance_convertisseur_appareils_w": commun["puissance_convertisseur_appareils_w"],
            },
        }



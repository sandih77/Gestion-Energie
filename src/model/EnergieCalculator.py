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
    def _window_peak_power_w(utilisations, window_start, window_end):
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
    def calculate_dimensionnement(matin_yield_pct=40.0, fa_yield_pct=20.0, battery_margin_pct=50.0):
        utilisations = Utilisation.get_all()

        battery_theoretical_wh = EnergieCalculator._window_energy_wh(
            utilisations,
            EnergieCalculator.SOIREE_WINDOW[0],
            EnergieCalculator.SOIREE_WINDOW[1],
        )

        panel_morning_theoretical_w = EnergieCalculator._window_peak_power_w(
            utilisations,
            EnergieCalculator.MATIN_WINDOW[0],
            EnergieCalculator.MATIN_WINDOW[1],
        )
        panel_fa_theoretical_w = EnergieCalculator._window_peak_power_w(
            utilisations,
            EnergieCalculator.FA_WINDOW[0],
            EnergieCalculator.FA_WINDOW[1],
        )

        matin_yield = max(EnergieCalculator._normalize_percentage(matin_yield_pct, 40.0), 0.0)
        fa_yield = max(EnergieCalculator._normalize_percentage(fa_yield_pct, 20.0), 0.0)
        battery_margin = max(EnergieCalculator._normalize_percentage(battery_margin_pct, 50.0), 0.0)

        panel_morning_practical_w = round(panel_morning_theoretical_w / (matin_yield / 100.0), 2) if matin_yield > 0 else 0.0
        panel_fa_practical_w = round(panel_fa_theoretical_w / (matin_yield / 100.0) / (fa_yield / 100), 2) if fa_yield > 0 else 0.0

        panel_required_w = round(max(panel_morning_practical_w, panel_fa_practical_w), 2)
        battery_practical_wh = round(battery_theoretical_wh * (1.0 + battery_margin / 100.0), 2)

        return {
            "battery_theoretical_wh": battery_theoretical_wh,
            "battery_practical_wh": battery_practical_wh,
            "battery_margin_pct": battery_margin,
            "panel_morning_theoretical_w": panel_morning_theoretical_w,
            "panel_morning_practical_w": panel_morning_practical_w,
            "panel_fa_theoretical_w": panel_fa_theoretical_w,
            "panel_fa_practical_w": panel_fa_practical_w,
            "panel_required_w": panel_required_w,
            "matin_yield_pct": matin_yield,
            "fa_yield_pct": fa_yield,
        }



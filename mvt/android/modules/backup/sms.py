# Mobile Verification Toolkit (MVT)
# Copyright (c) 2021-2023 Claudio Guarnieri.
# Use of this software is governed by the MVT License 1.1 that can be found at
#   https://license.mvt.re/1.1/

import logging
from typing import Optional

from mvt.android.modules.backup.base import BackupExtraction
from mvt.android.parsers.backup import parse_sms_file


class SMS(BackupExtraction):

    def __init__(
        self,
        file_path: Optional[str] = None,
        target_path: Optional[str] = None,
        results_path: Optional[str] = None,
        fast_mode: Optional[bool] = False,
        log: logging.Logger = logging.getLogger(__name__),
        results: Optional[list] = None
    ) -> None:
        super().__init__(file_path=file_path, target_path=target_path,
                         results_path=results_path, fast_mode=fast_mode,
                         log=log, results=results)
        self.results = []

    def check_indicators(self) -> None:
        if not self.indicators:
            return

        for message in self.results:
            if "body" not in message:
                continue

            if self.indicators.check_domains(message["links"]):
                self.detected.append(message)

    def run(self) -> None:
        sms_path = "apps/com.android.providers.telephony/d_f/*_sms_backup"
        for file in self._get_files_by_pattern(sms_path):
            self.log.info("Processing SMS backup file at %s", file)
            data = self._get_file_content(file)
            self.results.extend(parse_sms_file(data))

        mms_path = "apps/com.android.providers.telephony/d_f/*_mms_backup"
        for file in self._get_files_by_pattern(mms_path):
            self.log.info("Processing MMS backup file at %s", file)
            data = self._get_file_content(file)
            self.results.extend(parse_sms_file(data))

        self.log.info("Extracted a total of %d SMS & MMS messages containing links",
                      len(self.results))

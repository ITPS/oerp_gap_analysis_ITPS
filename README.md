Gap Analysis Module for OpenERP v7
=================

This Gap Analysis will provide actionable information about how an organization's technology and operations meet their current and future needs. It will indicate how OpenERP will match those needs and to allow the customer to determine the feasibility of implementing OpenERP. This Gap Analysis will be able to determine an estimate of project time and cost at ~70% certainty. It is also the first phase that allows the Customer to exit the project with limited investment if the results do not conform to their expectations. This results of this Gap Analysis will save time by allowing adequate planning for implementation leading to a smooth transition to OpenERP or any other software service.

There are 4 different modules which cover several aspect of the gap analysis:
• gap_analysis: main core of the gap analysis functionality (setup, import/export).
• gap_analysis_aeroo_report: allows the reporting in aeroo
• gap_analysis_project: necessary to generate the project from the gap analysis
• gap_analysis_project_long_term: necessary to generate the project from the gap analysis (with phasing)

An updated version of the module is available at:
• https://github.com/ITPS/oerp_gap_analysis_ITPS

Setup and Definitions - GAP Analysis elements

• Control – If the customer needs it then put Keep in it. If customer thinks it not necessary then Drop

• Category – Every functionality needs a category. This can be generated while entering the functionality directly or during a setup or configuration screen

• Functionality: short description (will be used in the task name when creating
   the project)

• Description – Describe full details of the functionality (will be included as
     description in the task.

• Critical Level – a score between 1 and 4 that represents the importance of
     the requirement for the contributors
1: Nice to have
2: Customer system is available and should be used
3: Very useful
4: Critical to the company

• Phase – Identify this task should done in which project phase. Phases are
create on the fly when creating the project

• Contributors – Names of the interested parties providing the functionality

• OpenERP Solution Mapping – Which OpenERP module can be used for this task.

• Identity the time may spend on those (in hours ): Basic Reports, Advanced Reports, Basic Processes, Advanced Processes, Basic Screens, Advanced Screens, Basic Workflows, Advanced Workflows, Access Rights Grops, Objects, Calculated Fields, Basic Wizards, Advanced Wizards

• Effort – a score between 1 and 5 that represents the effort it would take OpenERP Inc. to implement the requirement.
1:Feature already exists as is in OpenERP, Can be down in one hour;
2:Feature already exists in OpenERP and requires configuration (like a rule or a switch), no development involved, however may need more time which about two hours
3:Feature doesn't exist in OpenERP and requires a small (less than 4 hours)
custom development (no change in the existing logic);
4:Feature doesn't exist in OpenERP and either requires a heavy custom development (more than 4 hours) like a new module or a change in the existing logic;
5:Not enough information to identify the necessary development we need more detail

If you have any questions on this document you can contact:
• Nicholas Riegel (CEO at ITpedia Solutions LLC): nriegel@itpedia-solutions.com, 443-574-4877, Skype:itpedia
